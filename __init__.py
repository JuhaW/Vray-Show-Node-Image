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


def my_preview_update(self, context):
	Replace_Image.active_node = False
	Replace_Image.execute(self, context)

	
def node_has_texture(node):
	
	return hasattr(node,'vray_plugin') and hasattr(node, 'texture') and hasattr(node.texture, 'image')
		
def node_image_change():
	area = [i for i in bpy.context.screen.areas if i.type == 'NODE_EDITOR'][0]
	nodes = [i for i in area.spaces.active.node_tree.nodes if i.select]

	for node in nodes:
		
		if node_has_texture(node):
			#print ("node change:",node)
			
			if Replace_Image.active_node:
				node_active = area.spaces.active.node_tree.nodes.active
				node_active.texture.image = bpy.data.images[bpy.context.window_manager.my_previews]
				Replace_Image.active_node = False
				return
			else:
				node.texture.image = bpy.data.images[bpy.context.window_manager.my_previews]

############################################################################
class Active_Image_Node(bpy.types.Operator):
	bl_idname = 'active_image_node.operator'
	bl_label = "Show Image"
	bl_description = "Show selected image node image"	
	'''
	@classmethod
	def poll(cls, context):
		#print("poll")
		c = context.area.spaces.active
		#node editor, nodes exist,selected node has texture, image preview list == bpy.data.images.name
		#print(bpy.context.screen.areas[3].regions[1].type)
		if c.type == 'NODE_EDITOR' and hasattr(c.node_tree,'nodes'):
			selected_nodes = [i for i in c.node_tree.nodes if i.select]
			#print ("selected nodes:",selected_nodes)
			imagenames = [i.name for i in bpy.data.images if i.type == 'IMAGE']
			preview_imagenames = list(preview_collections["main"])
			difference = list(set(imagenames) ^ set(preview_imagenames))
			if difference:
				#print ("difference found !")
				Refresh.execute(Refresh,context)
				return False
			for node in selected_nodes:
				if node_has_texture(node):
					#print ("node has image texture")
					#image is in image preview list ? just loaded new image for example is not there
					
					if node.texture.image.name in bpy.data.images:
						if context.scene.auto_show_image:
							context.window_manager.my_previews = node.texture.image.name
							#preview_collections["main"].my_preview = node.texture.image.name
							#print()
							#print("poll successed")
							return True
					
						return True
					else:
						return false
			return False
		else:
			pass
			#print ("not node editor or no nodes on nodetree")
		return False
	'''
	def invoke(self, context, event):
		#print ("invoke event type:", event.type)
		return self.execute(context)	

	def execute(self, context):
		
		#image is in bpy.data.images ? just loaded new image for example

		c = context.area.spaces.active
		
		selected_nodes = [i for i in c.node_tree.nodes if i.select]

		for node in selected_nodes:
			if node_has_texture(node):
				
				#print()
				#print("node image name:", node.texture.image.name)
				#print()
				context.window_manager.my_previews = node.texture.image.name
				return {'FINISHED'}	
			else:
				#Refresh.execute(self, context)
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
		#print ("replace poll")
		c = context.area.spaces.active
		Replace_Image.image_nodes = 0

		if c.type == 'NODE_EDITOR' and hasattr(c.node_tree,'nodes'):
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
	kmi = km.keymap_items.new('active_image_node.operator', 'RIGHTMOUSE', 'CLICK')


def unregister():
	
	from bpy.types import WindowManager

	del WindowManager.my_previews

	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()
	
	bpy.utils.unregister_module(__name__)
	
	#bpy.utils.unregister_class(PreviewsExamplePanel)
	#bpy.utils.unregister_class(Test)

	#Remove keyboard shortcut configuration
	kc = bpy.context.window_manager.keyconfigs.addon
	km = kc.keymaps['Node Editor']
	km.keymap_items.remove(km.keymap_items['active_image_node.operator'])


if __name__ == "__main__":
	register()
