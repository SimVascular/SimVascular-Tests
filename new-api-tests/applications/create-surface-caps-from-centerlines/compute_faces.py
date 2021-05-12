#!/usr/bin/env python

'''This script attempts to determine the flat regions for a surface.
'''
import sys
import sv
import os
import vtk
from collections import defaultdict
from surface import Surface
from collections import OrderedDict

sys.path.insert(1, '../../../graphics/')
import graphics as gr

def get_connected_cells(cell_id, cell_normal, cell_adj, cell_edges, normals, cell_visited, level_num):
    #print('\n========== get_connected_cells adj_cell_id: {0:d} =========='.format(cell_id))
    tol = 0.99
    #print('[get_connected_cells] cell_normal: {0:s} '.format(str(cell_normal)))
    all_conn_cells = set()
    level_num += 1

    if cell_id in cell_visited or level_num > 500:
        return all_conn_cells

    all_conn_cells.add(cell_id)
    cell_visited.add(cell_id)
    conn_cells = set()

    for edge in cell_edges[cell_id]:
        cell_list = cell_adj[edge]
        for cid in cell_list:
            if cid == cell_id or cid in cell_visited:
                continue
            normal = [ normals.GetComponent(cid,i) for i in range(3)]
            dp = sum([cell_normal[k]*normal[k] for k in range(3)])
            #print('[get_connected_cells] cid {0:d}  normal: {1:s}  dp: {2:g}'.format(cid, str(cell_normal), dp))
            if dp >= tol:
                conn_cells.add(cid)
        #_for cid in cell_list
    #_for edge in cell_edges[cell_id]
    #print('[get_connected_cells] conn_cells: {0:s} '.format(str(conn_cells)))

    for cid in conn_cells:
        all_conn_cells.add(cid)
        new_conn_cells = get_connected_cells(cid, cell_normal, cell_adj, cell_edges, normals, cell_visited, level_num)
        #print('[get_connected_cells] new_conn_cells: {0:s} '.format(str(new_conn_cells)))
        for new_cid in new_conn_cells: 
            all_conn_cells.add(new_cid)

    #print('[get_connected_cells] all_conn_cells: {0:s} '.format(str(all_conn_cells)))
    return all_conn_cells

def show_region(renderer, surface, conn_cells, color):
    points = surface.GetPoints()
    radius = 0.05
    for cell_id in conn_cells:
        #print('----- cell {0:d} -----'.format(i))
        cell = surface.GetCell(cell_id)
        cell_pids = cell.GetPointIds()
        pid1 = cell_pids.GetId(0)
        pt1 = points.GetPoint(pid1)
        pid2 = cell_pids.GetId(1)
        pt2 = points.GetPoint(pid2)
        pid3 = cell_pids.GetId(2)
        pt3 = points.GetPoint(pid3)
        center = [(pt1[i] + pt2[i] + pt3[i]) / 3.0 for i in range(3)]
        gr.add_sphere(renderer, center, radius, color=color, wire=True)

def compute_faces(renderer, surface):
    print('========== compute_faces ==========')
    surface.BuildLinks()
    num_points = surface.GetNumberOfPoints()
    num_cells = surface.GetNumberOfCells()
    points = surface.GetPoints()
    normals = surface.GetCellData().GetArray('Normals')

    ## Build cell adjacency table.
    #
    cell_adj = defaultdict(set)
    cell_edges = defaultdict(set)

    for i in range(num_cells):
        #print('----- cell {0:d} -----'.format(i))
        cell = surface.GetCell(i)
        cell_pids = cell.GetPointIds()
        num_edges = cell.GetNumberOfEdges()
        #print('[compute_faces] num_edges: {0:d}'.format(num_edges))
        #print('[compute_faces] cell_pids: {0:s}'.format(str(cell_pids)))
        cell_normal = [ normals.GetComponent(i,j) for j in range(3)]
        #print('[compute_faces] normal: {0:s}'.format(str(cell_normal)))
        for j in range(num_edges):
            edge = cell.GetEdge(j)
            edge_ids = edge.GetPointIds()
            pid1 = edge_ids.GetId(0)
            pid2 = edge_ids.GetId(1)
            if pid1 > pid2:
                min_pid = pid2
                max_pid = pid1
            else:
                min_pid = pid1
                max_pid = pid2
            cell_adj[(min_pid,max_pid)].add(i)
            cell_edges[i].add((min_pid,max_pid))
            #print('[compute_faces] edge: {0:d} {1:d}'.format(pid1, pid2))
        #_for j in range(num_edges):
    #_for i in range(num_cells)

    normal = 3*[0.0]
    cell_regions = defaultdict(set)
    cell_visited = set()

    ## Determine regions.
    #
    print('Number of cells {0:d} '.format(num_cells))
    cell_count = 0
    level_num = 0
    regions = {}
    region_sizes = defaultdict(int)
    num_regions = 0
    max_region = 0
    max_region_size = 0

    for i in range(num_cells):
    #for i in range(20):
        if i in cell_visited:
            continue 
        #print('\n---------- cell {0:d} ----------'.format(i))
        cell_normal = [ normals.GetComponent(i,j) for j in range(3)]
        conn_cells = get_connected_cells(i, cell_normal, cell_adj, cell_edges, normals, cell_visited, level_num)
        if len(conn_cells) > 50:
            #print('\n---------- cell {0:d} ----------'.format(i))
            #print('conn_cells {0:d}  {1:s}'.format(len(conn_cells), str(conn_cells)))
            #show_region(renderer, surface, conn_cells)
            regions[i] = conn_cells 
            region_sizes[i] = len(conn_cells)
            if len(conn_cells) > max_region_size:
                max_region_size = len(conn_cells)
                max_region = i
            num_regions += 1
        cell_count += len(conn_cells)
        #_for edge in cell_edges[i]
    #_for i in range(num_cells)
    print('cell count: {0:d} '.format(cell_count))
    print('max_region: {0:d} '.format(max_region))
    print('max_region_size: {0:d} '.format(max_region_size))
    #show_region(renderer, surface, regions[max_region])

    #region_sizes_sorted = OrderedDict(sorted(region_sizes.items(), key=lambda x: x[1], reverse=True))
    #sorted(region_sizes.items(), key=lambda x: x[1], reverse=False)
    #for cid in region_sizes_sorted:
    #    print('region_sizes_sorted[0]: cid:{0:d}  size:{0:d} '.format(cid, region_sizes_sorted[cid]))

    region_count = 1
    for w in sorted(region_sizes, key=region_sizes.get, reverse=True):
        if region_count == 5:
           break
        print('region: {0:d}  cid: {1:d}  size: {2:d}'.format(region_count, w, region_sizes[w]))
        if region_count == 1:
            conn_cells = regions[w]
            #print('conn_cells {0:d}  {1:s}'.format(len(conn_cells), str(conn_cells)))
            show_region(renderer, surface, regions[w], color=[1,0,0])
        if region_count == 2:
            show_region(renderer, surface, regions[w], color=[0,1,0])
        if region_count == 3:
            show_region(renderer, surface, regions[w], color=[0,0,1])
        if region_count == 4:
            show_region(renderer, surface, regions[w], color=[0.5,0.51,0.51])
        region_count += 1

if __name__ == '__main__':
    file_name = sys.argv[1]
    file_prefix, file_extension = os.path.splitext(file_name)

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Read in surface.
    surface = Surface()
    surface.read(file_name)
    model_polydata = surface.geometry
    gr_geom = gr.add_geometry(renderer, model_polydata, color=[0.8, 0.8, 8.0])

    print("Num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
    print("Num cells: {0:d}".format(model_polydata.GetNumberOfCells()))

    compute_faces(renderer, model_polydata)

    ## Display window.
    gr.display(renderer_window)

