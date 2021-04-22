#!/usr/bin/env python
"""This script displays centerlines. 
"""
import argparse
from collections import defaultdict
import os
import sys
import vtk

sys.path.insert(1, '../../../graphics/')
import graphics as gr

test_id = 5

def get_end_points(renderer, lut, centerlines):
    num_lines = centerlines.GetNumberOfLines()
    id_hash = defaultdict(int)
    for i in range(num_lines):
        cell = centerlines.GetCell(i)
        cell_pids = cell.GetPointIds()
        num_ids = cell_pids.GetNumberOfIds()
        pid1 = cell_pids.GetId(0)
        pid2 = cell_pids.GetId(1)
        id_hash[pid1] += 1
        id_hash[pid2] += 1

    points = centerlines.GetPoints()
    end_ids = []

    for pid in id_hash:
        if id_hash[pid] == 1:
            #print("get_end_points] End point: {0:d}".format(pid))
            end_ids.append(pid)
            #pt = points.GetPoint(pid)
            #gr.add_sphere(renderer, pt, 0.5, color=[1,1,1], wire=True)

    return end_ids

def extract_data(renderer, lut, centerlines):
    print("---------- extract_data ----------")
    data_array = centerlines.GetPointData().GetArray('CenterlineId')
    num_centerlines = get_centerline_info(centerlines)
    min_id = 0
    max_id = num_centerlines-1
    cid_list = list(range(min_id,max_id+1))

    max_radius_data = centerlines.GetPointData().GetArray('MaximumInscribedSphereRadius')
    num_lines = centerlines.GetNumberOfLines()
    num_points = centerlines.GetNumberOfPoints()
    points = centerlines.GetPoints()
    print("Number of centerline lines: {0:d}".format(num_lines))

    #pt = points.GetPoint(0)
    #gr.add_sphere(renderer, pt, 0.5, color=[1,1,1], wire=True)

    max_num_lines = 0
    longest_cid = None
    for cid in range(min_id,max_id+1):
        section = extract_centerline(centerlines, cid)
        if section.GetNumberOfLines() > max_num_lines:
            max_num_lines = section.GetNumberOfLines()
            longest_cid = cid

    print("Longest cid: {0:d}".format(longest_cid))
    cell_cids = defaultdict(list)

    for cid in cid_list:
        #print("\n---------- cid {0:d} ----------".format(cid))
        for i in range(num_lines):
            cell = centerlines.GetCell(i)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            pid1 = cell_pids.GetId(0)
            pid2 = cell_pids.GetId(1)
            value1 = int(data_array.GetComponent(pid1, cid))
            value2 = int(data_array.GetComponent(pid2, cid))
            if (value1 == 1) or (value2 == 1):
                cell_cids[i].append(cid)
            #_for j in range(num_ids)
        #_for i in range(num_lines)
    #_for cid in range(min_id,max_id+1)

    cell_mask = vtk.vtkIntArray()
    cell_mask.SetNumberOfValues(num_lines)
    cell_mask.SetName("CellMask")
    centerlines.GetCellData().AddArray(cell_mask)

    branch_cells = defaultdict(list)
    radius = 0.4
    radius = 0.1
    #cid_list.remove(longest_cid)
    
    for cid in cid_list:
        #print("\n---------- find start cid {0:d} ----------".format(cid))
        for i in range(num_lines):
            cids = cell_cids[i]
            if longest_cid in cids:
            #if (longest_cid in cids) and (i not in branch_cells[longest_cid]):
                if i not in branch_cells[longest_cid]:
                    branch_cells[longest_cid].append(i)
            else:
                if (len(cids) == 1) and (cids[0] == cid):
                    branch_cells[cid].append(i)
                if cid in cell_cids[i]:
                    cell_cids[i].remove(cid)
            #_for j in range(num_ids)
        #show_branch(renderer, lut, centerlines, cid, branch_cells, radius)
    #_for cid in cid_list

    end_point_ids = get_end_points(renderer, lut, centerlines)

    #for cid in [longest_cid]:
    for cid in cid_list:
        create_branch(renderer, lut, centerlines, cid, branch_cells, radius, end_point_ids)

    '''
    for i in range(num_lines):
        cids = cell_cids[i]
        if longest_cid in cids:
            branch_cells[longest_cid].append(i)
    show_branch(renderer, lut, centerlines, longest_cid, branch_cells, radius)
    '''

def create_branch(renderer, lut, centerlines, cid, branch_cells, radius, end_point_ids):
    print("\n---------- create_branch cid {0:d} ----------".format(cid))
    points = centerlines.GetPoints()
    num_lines = centerlines.GetNumberOfLines()
    point_ids = set()
    start_cell = None
    start_ids = []

    for i,cell_id in enumerate(branch_cells[cid]):
        #print("[create_branch] cell_id: {0:d}".format(cell_id))
        #print("[create_branch]    pid1: {0:d}  pid2: {1:d}".format(pid1 ,pid2))
        cell = centerlines.GetCell(cell_id)
        cell_pids = cell.GetPointIds()
        num_ids = cell_pids.GetNumberOfIds()
        pid1 = cell_pids.GetId(0)
        pid2 = cell_pids.GetId(1)
        point_ids.add(pid1)
        point_ids.add(pid2)
        if pid1 in end_point_ids:
            start_cell = cell_id
            start_ids.append(pid1)
            #print("[create_branch] i: {0:d}".format(i))
            #print("[create_branch] cell_id: {0:d}".format(cell_id))
            #print("[create_branch]    1) pid1: {0:d}  pid2: {1:d}".format(pid1 ,pid2))
        elif pid2 in end_point_ids:
            start_cell = cell_id
            start_ids.append(pid2)
            #print("[create_branch] i: {0:d}".format(i))
            #print("[create_branch] cell_id: {0:d}".format(cell_id))
            #print("[create_branch]    2) pid1: {0:d}  pid2: {1:d}".format(pid1 ,pid2))

    num_points = len(point_ids)
    print("[create_branch] Number of point IDs: {0:d}".format(num_points))
    print("[create_branch] Start cell: {0:d}".format(start_cell))
    print("[create_branch] Start point IDs: {0:s}".format(str(start_ids)))

    if len(start_ids) == 2:
        if start_ids[0] < start_ids[1]:
            start_id = start_ids[0]
        else:
            start_id = start_ids[1]
    else:
        start_id = start_ids[0]

    start_pt = points.GetPoint(start_id)
    color = [0.0, 0.0, 0.0]
    lut.GetColor(cid, color)
    gr.add_sphere(renderer, start_pt, radius, color=color, wire=True)

def show_branch(renderer, lut, centerlines, cid, branch_cells, radius):
    num_lines = centerlines.GetNumberOfLines()
    cell_mask = centerlines.GetCellData().GetArray("CellMask")

    for i in range(num_lines):
        cell_mask.SetValue(i,0);

    for cell_id in branch_cells[cid]:
        cell_mask.SetValue(cell_id,1);

    color = [0.0, 0.0, 0.0]
    lut.GetColor(cid, color)

    points = centerlines.GetPoints()
    cell_id = branch_cells[cid][0]
    cell = centerlines.GetCell(cell_id)
    cell_pids = cell.GetPointIds()
    pid = cell_pids.GetId(0)
    start_pt = points.GetPoint(pid)
    gr.add_sphere(renderer, start_pt, radius, color=color, wire=True)
    #print("Start cell ID: {0:d}".format(cell_id))
    #print("Start point ID: {0:d}".format(pid))

    cell_id = branch_cells[cid][-1]
    cell = centerlines.GetCell(cell_id)
    cell_pids = cell.GetPointIds()
    pid = cell_pids.GetId(0)
    end_pt = points.GetPoint(pid)
    gr.add_sphere(renderer, end_pt, radius, color=color, wire=False)
    #print("End cell ID: {0:d}".format(cell_id))
    #print("End point ID: {0:d}".format(pid))

    thresh = vtk.vtkThreshold()
    thresh.SetInputData(centerlines)
    thresh.ThresholdBetween(1, 1)
    thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", "CellMask")
    thresh.Update()

    surfacefilter = vtk.vtkDataSetSurfaceFilter()
    surfacefilter.SetInputData(thresh.GetOutput())
    surfacefilter.Update()
    branch_geom = surfacefilter.GetOutput()
    gr.add_geometry(renderer, branch_geom, color=color, line_width=4)
    return branch_geom 

def extract_centerline(centerlines, cid):
    data_array = centerlines.GetPointData().GetArray('CenterlineId')
    thresh = vtk.vtkThreshold()
    thresh.SetInputData(centerlines)
    thresh.ThresholdBetween(1.0, 1.0)
    thresh.SetComponentModeToUseSelected()
    thresh.SetSelectedComponent(cid)
    #thresh.SetPassThroughCellIds(cell_ids)
    thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_POINTS", 'CenterlineId')
    thresh.Update()

    surfacefilter = vtk.vtkDataSetSurfaceFilter()
    surfacefilter.SetInputData(thresh.GetOutput())
    surfacefilter.Update()
    return surfacefilter.GetOutput()

def get_centerline_info(centerlines):
    data_array = centerlines.GetPointData().GetArray('CenterlineId')
    num_comp = data_array.GetNumberOfComponents()
    print("[get_centerline_info] num_comp: " + str(num_comp))
    return num_comp 

def get_branch_info(centerlines, array_name):
    branch_id_array = centerlines.GetPointData().GetArray(array_name)
    vrange = branch_id_array.GetRange()
    min_id = int(vrange[0])
    max_id = int(vrange[1])
    print("[get_branch_info] Min id: " + str(min_id))
    print("[get_branch_info] Max id: " + str(max_id))
    return min_id, max_id

def find_common_points(branch1, branch2):
    print("========== find_common_points ==========")
    num_points1 = branch1.GetNumberOfPoints()
    points1 = branch1.GetPoints()
    num_points2 = branch2.GetNumberOfPoints()
    points2 = branch2.GetPoints()

    print("branch1: num points: {0:d}".format(num_points1))
    print("branch2: num points: {0:d}".format(num_points2))

    min_d = 1e6
    min_i = None
    min_j = None
    min_pt = None

    for i in range(num_points1):
        pt1 = points1.GetPoint(i)
        for j in range(num_points2):
            pt2 = points2.GetPoint(j)
            d = sum([(pt1[k] - pt2[k]) * (pt1[k] - pt2[k]) for k in range(3)])
            if d < min_d:
                min_d = d
                min_i = i
                min_j = j
                min_pt = pt2
    #_for i in range(num_points1)

    print("min_d: {0:g} ".format(min_d))
    print("min_i: {0:d} ".format(min_i))
    print("min_j: {0:d} ".format(min_j))
    print("min_pt: {0:s} ".format(str(min_pt)))
    return min_pt

def extract_sections(centerlines, cid, array_name):
    '''Extract a section of the centerlines geometry for the given ID.
    '''
    thresh = vtk.vtkThreshold()
    thresh.SetInputData(centerlines)
    thresh.ThresholdBetween(cid, cid)
    thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_POINTS", array_name)
    #thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", array_name)
    thresh.Update()

    surfacefilter = vtk.vtkDataSetSurfaceFilter()
    surfacefilter.SetInputData(thresh.GetOutput())
    surfacefilter.Update()
    return surfacefilter.GetOutput()

if __name__ == '__main__':
    file_name = sys.argv[1]

    # Read centerlines.
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    centerlines = reader.GetOutput()

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)
    gr_geom = gr.add_geometry(renderer, centerlines, color=[1.0, 1.0, 1.0], line_width=1)

    num_centerlines = get_centerline_info(centerlines)
    min_id = 0
    max_id = num_centerlines-1

    # Create a color lookup table.
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(min_id, max_id+1)
    lut.SetHueRange(0, 1)
    lut.SetSaturationRange(1, 1)
    lut.SetValueRange(1, 1)
    lut.Build()

    extract_data(renderer, lut, centerlines)

    # Extract centerlines.
    radius = 1.1
    radius = 0.05
 
    '''
    for cid in range(min_id,max_id+1):
        color = [0.0, 0.0, 0.0]
        lut.GetColor(cid, color)
        if cid == test_id:
        #if cid >= 0:
            centerline = extract_centerline(centerlines, cid)
            gr.add_geometry(renderer, centerline, color=color, line_width=2)
    '''

    '''
    # Get min/max branch IDs.
    array_name = 'BranchId'
    array_name = 'BranchIdTmp'
    min_id, max_id = get_branch_info(centerlines, array_name)

    # Create a color lookup table.
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(min_id, max_id+1)
    lut.SetHueRange(0, 1)
    lut.SetSaturationRange(1, 1)
    lut.SetValueRange(1, 1)
    lut.Build()

    # Extract branches.
    radius = 1.1
    radius = 0.05
    for bid in range(min_id,max_id+1):
        branch = extract_sections(centerlines, bid, array_name)
        color = [0.0, 0.0, 0.0]
        lut.GetColor(bid, color)
        gr.add_geometry(renderer, branch, color=color, line_width=2)

        num_points = branch.GetNumberOfPoints()
        points = branch.GetPoints()
        start_pt = points.GetPoint(0)
        end_pt = points.GetPoint(num_points-1)
        num_lines = branch.GetNumberOfLines()

        if bid == 20:
        #if bid >= 0:
        #if bid == 0:
            print("Branch {0:d}".format(bid))
            print(" num_pts: {0:d}".format(num_points))
            print(" num_lines: {0:d}".format(num_lines))
            #gr.add_sphere(renderer, start_pt, radius, color=color, wire=True)
            #gr.add_sphere(renderer, end_pt, radius, color=color)
            #break

    '''

    ## Display window.
    gr.display(renderer_window)

