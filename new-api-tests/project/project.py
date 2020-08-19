
import collections
import os
import glob
import sv 
from image import Image 

class ProjectPluginNames(object):
    ''' This class stores the names of SV plugin categories.
    '''
    IMAGES = "Images"
    MESHES = "Meshes"
    MODELS = "Models"
    PATHS = "Paths"
    SEGMENTATIONS = "Segmentations"
    SIMULATIONS = "Simulations"
    names = [ IMAGES, MESHES, MODELS, PATHS, SEGMENTATIONS, SIMULATIONS ]

class ProjectPluginInstance(object):
    ''' This class stores the names and file name for an instance of an SV plugin.
    '''
    def __init__(self, name, file_name):
        self.name = name 
        self.file_name = file_name 

class ProjectPlugin(object):
    ''' This class stores the the plugin instances for an SV plugin category.
    '''
    def __init__(self, name):
        self.name = name 
        self.instances = None
        self.file_extension = None

    def get_files(self, project_dir):
        ''' Get the names of the files defined for each plugin.
        '''
        #print("[ProjectPlugin.read_files] Plugin directory: {0:s}".format(self.name))
        #print("[ProjectPlugin.read_files]   File extension: {0:s}".format(self.file_extension))
        rep = project_dir+"/"+self.name+"/*."+self.file_extension
        pfiles = [f for f in glob.glob(rep)]
        #print("[ProjectPlugin.read_files] Files: {0:s}".format(str(files)))
        if len(pfiles) > 0:
            self.instances = []
        for pfile in pfiles:
            base = os.path.basename(pfile)
            name = os.path.splitext(base)[0]
            #print("[ProjectPlugin.read_files]   Instance: {0:s}".format(str(name)))
            self.instances.append( ProjectPluginInstance(name, pfile) )

    def get_plugin_instances(self):
        if self.instances == None:
            return []
        return [inst.name for inst in self.instances] 
        #return ', '.join([inst.name for inst in self.instances]) 

class ProjectImagesPlugin(ProjectPlugin):
    def __init__(self):
        super().__init__(ProjectPluginNames.IMAGES)
        self.file_extension = 'vti'

    def get_image(self, name):
        print("[ProjectImagesPlugin.get_model] Name: {0:s}".format(name))
        instance = None
        for inst in self.instances:
            if name == inst.name:
                instance = inst
        if instance == None:
            print("[ProjectImagesPlugin.get_image] ERROR: Name {0:s} not found.".format(name))
            return None
        print("[ProjectImagesPlugin.get_image] Read image file: {0:s}".format(instance.file_name))
        image = Image()
        image.read_volume(instance.file_name)
        return image

class ProjectMeshesPlugin(ProjectPlugin):
    def __init__(self):
        super().__init__(ProjectPluginNames.MESHES)
        self.file_extension = 'msh'

class ProjectModelsPlugin(ProjectPlugin):
    def __init__(self):
        super().__init__(ProjectPluginNames.MODELS)
        self.file_extension = 'mdl'

    def get_model(self, name):
        print("[ProjectModelsPlugin.get_model] Name: {0:s}".format(name))
        instance = None
        for inst in self.instances:
            if name == inst.name:
                instance = inst
        if instance == None:
            print("[ProjectModelsPlugin.get_model] ERROR: Name {0:s} not found.".format(name))
            return None
        print("[ProjectModelsPlugin.get_model] Read model file: {0:s}".format(instance.file_name))
        return sv.solid.Series(instance.file_name)

class ProjectPathsPlugin(ProjectPlugin):
    ''' This class is used to represent data for an SV Path plugin. 
    '''
    def __init__(self):
        super().__init__(ProjectPluginNames.PATHS)
        self.file_extension = 'pth'

    def get_path(self, name):
        print("[ProjectPathsPlugin.get_path] Name: {0:s}".format(name))
        instance = None
        for inst in self.instances:
            if name == inst.name:
                instance = inst
        if instance == None:
            print("[ProjectPathsPlugin.get_path] ERROR: Name {0:s} not found.".format(name))
            return None
        print("[ProjectPathsPlugin.get_path] Read path file: {0:s}".format(instance.file_name))
        return sv.pathplanning.Series(instance.file_name)

class ProjectSegmentationsPlugin(ProjectPlugin):
    def __init__(self):
        super().__init__(ProjectPluginNames.SEGMENTATIONS)
        self.file_extension = 'ctgr'

    def get_contour(self, name):
        print("[ProjectSegmentationsPlugin.get_contour] Name: {0:s}".format(name))
        instance = None
        for inst in self.instances:
            if name == inst.name:
                instance = inst
        if instance == None:
            print("[ProjectSegmentationsPlugin.get_contour] ERROR: Name {0:s} not found.".format(name))
            return None
        print("[ProjectSegmentationsPlugin.get_contour] Read contour file: {0:s}".format(instance.file_name))
        return sv.segmentation.Series(instance.file_name)

class ProjectSimulationsPlugin(ProjectPlugin):
    def __init__(self):
        super().__init__(ProjectPluginNames.SIMULATIONS)
        self.file_extension = 'sjb'

class Project(object):
    ''' This class is used to store an SV project. 
    '''
    def __init__(self):
        self.project_dir = None
        self.add_plugins()
        self.plugin_names = ProjectPluginNames()

    def add_plugins(self):
        self.images_plugin = ProjectImagesPlugin()
        self.meshes_plugin = ProjectMeshesPlugin()
        self.models_plugin = ProjectModelsPlugin()
        self.paths_plugin = ProjectPathsPlugin()
        self.segmentations_plugin = ProjectSegmentationsPlugin()
        self.simulations_plugin = ProjectSimulationsPlugin()

        # Create an ordered dict used to iterate over the pulgins.
        self.plugins = collections.OrderedDict()
        self.plugins[ProjectPluginNames.IMAGES] = self.images_plugin 
        self.plugins[ProjectPluginNames.MESHES] = self.meshes_plugin 
        self.plugins[ProjectPluginNames.MODELS] = self.models_plugin 
        self.plugins[ProjectPluginNames.PATHS] = self.paths_plugin 
        self.plugins[ProjectPluginNames.SEGMENTATIONS] = self.segmentations_plugin 
        self.plugins[ProjectPluginNames.SIMULATIONS] = self.simulations_plugin 
        '''
        for name,plugin in self.plugins.items():
            print("Plugin name: {0:s}".format(name))
            print("       name: {0:s}".format(plugin.name))
        '''

    def open(self, project_dir):
        print("[Project.open] Project directory: {0:s}".format(project_dir))
        self.project_dir = project_dir 
        for name,plugin in self.plugins.items():
            plugin.get_files(project_dir)

    def get_image(self, name):
        return self.images_plugin.get_image(name)

    def get_model(self, name):
        return self.models_plugin.get_model(name)

    def get_plugin_instances(self, plugin_name=None):
        if plugin_name == None: 
            plugin_instances = collections.OrderedDict()
            for name,plugin in self.plugins.items():
                plugin_instances[name] =  plugin.get_plugin_instances()
        else:
            plugin_instances = []
            for name,plugin in self.plugins.items():
                if name == plugin_name:
                    plugin_instances = plugin.get_plugin_instances() 
        return plugin_instances


    def get_path(self, name):
        return self.paths_plugin.get_path(name)

    def get_segmentation(self, name):
        return self.segmentations_plugin.get_contour(name)

