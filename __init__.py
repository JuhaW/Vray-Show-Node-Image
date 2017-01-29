# This sample script demonstrates a dynamic EnumProperty with custom icons.
# The EnumProperty is populated dynamically with thumbnails of the contents of
# a chosen directory in 'enum_previews_from_directory_items'.
# Then, the same enum is displayed with different interfaces. Note that the
# generated icon previews do not have Blender IDs, which means that they can
# not be used with UILayout templates that require IDs,
# such as template_list and template_ID_preview.
#
# Other use cases:
# - make a fixed list of enum_items instead of calculating them in a function
# - generate isolated thumbnails to use as custom icons in buttons
#	and menu items
#
# For custom icons, see the template "ui_previews_custom_icon.py".
#
# For distributable scripts, it is recommended to place the icons inside the
# script directory and access it relative to the py script file for portability:
#
#	 os.path.join(os.path.dirname(__file__), "images")
bl_info = {
	"name": "Vray View Image Node",
	"author": "JuhaW",
	"version": (0, 1),
	"blender": (2, 7, 8),
	"location": "",
	"description": "",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Node"
}

import os, time
import bpy
from bpy.props import BoolProperty, IntProperty
VRAY = True

#cycles
#bpy.context.object.active_material.node_tree.nodes.active.type = 'TEX_IMAGE'
#bpy.context.object.active_material.node_tree.nodes.active.image.filepath

def my_preview_update(self, context):
	Replace_Image.active_node = False
	Replace_Image.execute(self, context)

	
def node_has_texture(node):
	global VRAY
	if VRAY:
		return hasattr(node,'vray_plugin') and hasattr(node, 'texture') and hasattr(node.texture, 'image')
	else:
		return hasattr(node, 'image')

def node_set_image(node):
	global VRAY
	if VRAY:
		node.texture.image = bpy.data.images[bpy.context.window_manager.my_previews]
	else:
		node.image = bpy.data.images[bpy.context.window_manager.my_previews]

def node_image_change():
	area = [i for i in bpy.context.screen.areas if i.type == 'NODE_EDITOR'][0]
	nodes = [i for i in area.spaces.active.node_tree.nodes if i.select]

	for node in nodes:
		
		if node_has_texture(node):
			#print ("node change:",node)
			
			if Replace_Image.active_node:
				node_active = area.spaces.active.node_tree.nodes.active
				node_set_image(node_active)
				Replace_Image.active_node = False
				return
			else:
				node_set_image(node)

############################################################################
class image_fix_duplicates(bpy.types.Operator):
	bl_idname = 'image_fix_duplicates.operator'
	bl_label = "Fix duplicated images"
	bl_description = "Image names end with .001 .002 but the same filepath will be deleted and only one is shared between image nodes"	

#fix duplicated images, different name but the same image filepath
#delete duplicated images and replace image node images with that which have the same filepath
#


	def execute(self, context):
		global VRAY
		multi_images = []
		multi_filepaths = []
		for i in bpy.data.images:
			cnt = 0
			for j in bpy.data.images:
				if i.filepath == j.filepath:
					cnt += 1
					if cnt == 2:
						if i.filepath not in multi_filepaths:
							multi_images.append(i)
							multi_filepaths.append(i.filepath)

		print ("multi:",multi_images)
		print ("multi:",multi_filepaths)
		if VRAY:
			ngroups = [ng for ng in bpy.data.node_groups if ng.bl_idname == 'VRayNodeTreeMaterial']
		else:
			ngroups = [ng.node_tree for ng in bpy.data.materials if hasattr(ng.node_tree,'nodes')]

		for ng in ngroups:
			for node in ng.nodes:
				if node_has_texture(node):
					
					if VRAY:
						print (node.texture.image.filepath)
						if node.texture.image.filepath in multi_filepaths:
							node.texture.image = multi_images[multi_filepaths.index(node.texture.image.filepath)]
					else:
						print (node.image.filepath)
						if node.image.filepath in multi_filepaths:
							node.image = multi_images[multi_filepaths.index(node.image.filepath)]

		for i in bpy.data.images:
			cnt = 0
			for j in bpy.data.images:
				if i.filepath == j.filepath:
					cnt += 1
					if cnt > 1:
						bpy.data.images.remove(j)
		if cnt > 1:
			Refresh(self,context)
		return {'FINISHED'}	

class Active_Image_Node(bpy.types.Operator):
	bl_idname = 'active_image_node.operator'
	bl_label = "Show Image"
	bl_description = "Show selected image node image"	
	
	def execute(self, context):
		global VRAY
		c = context.area.spaces.active
		
		if not hasattr(c.node_tree,'nodes'):
			print("no nodes")
			return {'FINISHED'}

		selected_nodes = [i for i in c.node_tree.nodes if i.select]
		
		for node in selected_nodes:

			if node_has_texture(node):
				#print ("node:",node)
				if c.node_tree.nodes.active == node:
					#image is not in preview image list ? just loaded new image for example
					imagenames = [i.name for i in bpy.data.images if i.type == 'IMAGE']
					preview_imagenames = list(preview_collections["main"])
					difference = list(set(imagenames) ^ set(preview_imagenames))
					if difference:
						#print ("difference found !")
						Refresh.execute(Refresh,context)
						#return {'FINISHED'}
					if VRAY:
						context.window_manager.my_previews = node.texture.image.name
					else:
						context.window_manager.my_previews = node.image.name
					return {'FINISHED'}	
			
			
		return {'FINISHED'}		   


class Replace_Image(bpy.types.Operator):
	bl_idname = 'replace_image.operator'
	bl_label = "Replace"
	bl_description = "Replace selected image node images with selected image"
	
	image_nodes = IntProperty(default = 0)
	active_node = bpy.props.BoolProperty(default = False)

	@classmethod
	def poll(cls, context):
		global VRAY
		c = context.area.spaces.active
		if bpy.context.scene.render.engine.startswith('VRAY',0):
			VRAY = True
		else:
			VRAY = False

		Replace_Image.image_nodes = 0

		if c.type == 'NODE_EDITOR' and hasattr(c.node_tree,'nodes'):
			#print ("poll")
			selected_nodes = [i for i in c.node_tree.nodes if i.select]
			for node in selected_nodes:
				if node_has_texture(node):
					Replace_Image.image_nodes += 1

			#context.scene.image_nodes_selected = image_nodes
			
			if Replace_Image.image_nodes:
				return True
			
		else:
			return False

	def execute(self, context):
		#print("active_node",Replace_Image.active_node)
		#print(bpy.context.window_manager.my_previews)
		node_image_change()
		
		return {'FINISHED'}		   

class Refresh(bpy.types.Operator):
	bl_idname = 'refresh.operator'
	bl_label = "Refresh"
	bl_description ="Refresh image list"

	update = False		
	
	def execute(self, context):
		
		Refresh.update = True
		enum_previews_from_directory_items(self, context)
		
		return {'FINISHED'}		   

def enum_previews_from_directory_items(self, context):
	"""EnumProperty callback"""
	enum_items = []

	if context is None:
		return enum_items

	# Get the preview collection (defined in register func).
	pcoll = preview_collections["main"]
	
	if not Refresh.update:
		#print("No new collection created")
		
		return pcoll.my_previews
	else:
		##print
		#("#####################################################################New
		#collection created")
		Refresh.update = False
			
	
	pcoll.clear()
	images = [i for i in bpy.data.images if i.type == 'IMAGE']
	for i, name in enumerate(images):
		# generates a thumbnail preview for a file.
		#filepath = os.path.join(directory, name)
		thumb = pcoll.load(name.name, name.filepath, 'IMAGE')
		enum_items.append((name.name, name.name, "", thumb.icon_id, i))

	pcoll.my_previews = enum_items
	#pcoll.my_previews_dir = directory
	##print ("winman.my_previews", bpy.context.window_manager.my_previews)
	return pcoll.my_previews


class PreviewsExamplePanel(bpy.types.Panel):
	"""Creates a Panel in the Object properties window"""
	bl_label = "Image node"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Trees"
	
	bpy.types.Scene.auto_show_image = bpy.props.BoolProperty(default = True, description ="Show selected node image")
	bpy.types.Scene.image_nodes_selected = bpy.props.IntProperty(default = 0, description ="Image nodes selected")

	def draw(self, context):
		layout = self.layout
		wm = context.window_manager

		#row.prop(wm, "my_previews_dir")
		row = layout.row()
		row.template_icon_view(wm, "my_previews")

		row = layout.row()
		row.prop(wm, "my_previews", text = "Image")
		row = layout.row()
		a = row.operator('replace_image.operator', text = "Replace image", icon = 'NODETREE')
		a.active_node = False
		row.operator('refresh.operator', icon = 'FILE_REFRESH')
		#row.operator('active_image_node.operator', icon = 'IMAGE_DATA')
		
		row = layout.row()
		#row.prop(context.scene,'auto_show_image',text = "Auto show image")
		#row = layout.row()
		row.operator('image_fix_duplicates.operator', icon = 'GHOST')
		row = layout.row()

		cnt = Replace_Image.image_nodes
		row.label('{} Image node{} selected'.format(cnt,"" if cnt == 0 or cnt == 1 else "s" ))
		
		#print ("preview_collections['main']:", len(preview_collections['main']))
		'''
		ntree = context.object.active_material.vray.ntree # our custom node tree
		node = ntree.nodes.active # selected node
		for socket in node.outputs:
			layout.template_node_view(ntree, node, socket)
		'''
# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}


def register():
	
	from bpy.types import WindowManager
	from bpy.props import (
			StringProperty,
			EnumProperty,
			)
	
	WindowManager.my_previews_dir = StringProperty(name="Folder Path",
			subtype='DIR_PATH',
			default="")

	WindowManager.my_previews = EnumProperty(items=enum_previews_from_directory_items,update = my_preview_update)

	import bpy.utils.previews
	pcoll = bpy.utils.previews.new()
	pcoll.my_previews_dir = ""
	pcoll.my_previews = ()

	preview_collections["main"] = pcoll

	bpy.utils.register_module(__name__)
	#bpy.utils.register_class(PreviewsExamplePanel)
	#bpy.utils.register_class(Test)
	Refresh.update = True
	km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
	kmi = km.keymap_items.new('active_image_node.operator', 'LEFTMOUSE', 'CLICK')
	

def unregister():
	
	from bpy.types import WindowManager

	del WindowManager.my_previews

	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()
	
	#Remove keyboard shortcut configuration
	kc = bpy.context.window_manager.keyconfigs.addon
	km = kc.keymaps['Node Editor']
	km.keymap_items.remove(km.keymap_items['active_image_node.operator'])
	
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
