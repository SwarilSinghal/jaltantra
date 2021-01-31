# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PHED
								 A QGIS plugin
 This plugin generate PHED data in Jaltantra input format
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
							  -------------------
		begin                : 2020-10-12
		git sha              : $Format:%H$
		copyright            : (C) 2020 by Swaril Singhal
		email                : 305swaril@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QMenu, QInputDialog
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsWkbTypes, QgsVectorLayer, QgsApplication
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsPoint, QgsLayerTreeLayer
from qgis.core import QgsVectorDataProvider, QgsFeature, QgsGeometry, QgsField, QgsExpression
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMenu
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
from shapely.wkb import dumps, loads
# from processing.tools.vector import VectorWriter

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .PHED_dialog import PHEDDialog
import os.path
import ogr, osr,csv

class PHED:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'PHED_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)
			QCoreApplication.installTranslator(self.translator)

		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&PHED')

		# Check if plugin was started the first time in current QGIS session
		# Must be set in initGui() to survive plugin reloads
		self.first_start = None

	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('PHED', message)


	def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):
		"""Add a toolbar icon to the toolbar.

		:param icon_path: Path to the icon for this action. Can be a resource
			path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
		:type icon_path: str

		:param text: Text that should be shown in menu items for this action.
		:type text: str

		:param callback: Function to be called when the action is triggered.
		:type callback: function

		:param enabled_flag: A flag indicating if the action should be enabled
			by default. Defaults to True.
		:type enabled_flag: bool

		:param add_to_menu: Flag indicating whether the action should also
			be added to the menu. Defaults to True.
		:type add_to_menu: bool

		:param add_to_toolbar: Flag indicating whether the action should also
			be added to the toolbar. Defaults to True.
		:type add_to_toolbar: bool

		:param status_tip: Optional text to show in a popup when mouse pointer
			hovers over the action.
		:type status_tip: str

		:param parent: Parent widget for the new action. Defaults None.
		:type parent: QWidget

		:param whats_this: Optional text to show in the status bar when the
			mouse pointer hovers over the action.

		:returns: The action that was created. Note that the action is also
			added to self.actions list.
		:rtype: QAction
		"""

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			# Adds plugin icon to Plugins toolbar
			self.iface.addToolBarIcon(action)

		if add_to_menu:
			self.menu.addAction(action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/PHED/icon.png'
		self.menu = self.iface.mainWindow().findChild(QMenu, '&WNDS')
		# If the menu does not exist, create it!
		if not self.menu:
			self.menu = QMenu('&WNDS', self.iface.mainWindow().menuBar())
			self.menu.setObjectName('&WNDS')
			actions = self.iface.mainWindow().menuBar().actions()
			lastAction = actions[-1]
			self.iface.mainWindow().menuBar().insertMenu(lastAction, self.menu)
		self.add_action(
			icon_path,
			text=self.tr(u'PHED'),
			callback=self.run,
			parent=self.iface.mainWindow())

		# will be set False in run()
		self.first_start = True


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginMenu(
				self.tr(u'&PHED'),
				action)
			self.menu.removeAction(action)
			self.iface.removeToolBarIcon(action)

	def t0_Upload_Pipeline_Layer(self):
		pipes_file, _filter = QFileDialog.getSaveFileName(
			self.dlg, "Select  PipeLine file ", "", '*.shp')
		self.dlg.lineEdit_21.setText(pipes_file)
	def t1_Upload_Pipeline_Layer(self):
		pipes_file, _filter = QFileDialog.getSaveFileName(
			self.dlg, "Select  PipeLine file ", "", '*.shp')
		self.dlg.lineEdit_24.setText(pipes_file)
		# pipes_file = self.dlg.lineEdit_21.text()

		
	def t0_Upload_Node_Layer(self):
		proposed_nodes_file, _filter = QFileDialog.getOpenFileName(
			self.dlg, "Select  Nodelayer file ", "", '*.csv')
		self.dlg.lineEdit_22.setText(proposed_nodes_file)
	def t1_Upload_Node_Layer(self):
		proposed_nodes_file, _filter = QFileDialog.getOpenFileName(
			self.dlg, "Select  Nodelayer file ", "", '*.csv')
		self.dlg.lineEdit_23.setText(proposed_nodes_file)
		# proposed_nodes_file = self.dlg.lineEdit_22.text()
		# crs = QgsCoordinateReferenceSystem("epsg:4326")

		# PointLyr = QgsVectorLayer(proposed_nodes_file, "Nodes", "ogr")
		# uri = proposed_nodes_file + "?delimiter=%s&xField=%s&yField=%s&decimal=%s" % (",", "Longitude", "Latitude", ".")
		# layer = QgsVectorLayer(uri, "my_layer", "delimitedtext")
		# dir_path = os.path.dirname(proposed_nodes_file)
		# res_shap = dir_path + "/Nodes.shp"
		# QgsVectorFileWriter.writeAsVectorFormat(layer, res_shap, "UTF-8", crs, "ESRI Shapefile")
		# QgsProject.instance().addMapLayer(PointLyr)


	def t0_Update_Pipeline_Layer(self):
		nodes_file = self.dlg.lineEdit_22.text()
		# ogr2ogr.main(["","-f", "ESRI Shapefile", "-s_srs", "epsg:32643", "-t_srs", "epsg:4326", "newp.shp", nodes_file])
		nodeLyr = QgsVectorLayer(nodes_file, "nodes", "ogr")
		pipes_file = self.dlg.lineEdit_21.text()
		# ogr2ogr.main(["","-f", "ESRI Shapefile", "-s_srs", "epsg:32643", "-t_srs", "epsg:4326", "newl.shp", pipes_file])
		# pipeLyr = QgsVectorLayer(pipes_file, "updated pipes", "ogr")
		vl = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
		pr = vl.dataProvider()

		#setting up reprojection for temporary points
		epsg4326 = QgsCoordinateReferenceSystem(
			4326,
			QgsCoordinateReferenceSystem.EpsgCrsId)
		self.reprojectgeographic = QgsCoordinateTransform(
			self.iface.mapCanvas().mapSettings().destinationCrs(),
			epsg4326, QgsProject.instance())
		# Enter editing mode
		vl.startEditing()
		# add fields
		pr.addAttributes([
			QgsField("id", QVariant.Int),
			QgsField("Name", QVariant.String),
			# QgsField("Latitude", QVariant.String),
			# QgsField("Longuitude", QVariant.String),
			# QgsField("Coordinates", QVariant.String),
			QgsField("GL(m)", QVariant.String),
			# QgsField("Dem.(lps)", QVariant.Int),
			# QgsField("Active", QVariant.String),
			QgsField("Dem.(lps)", QVariant.String)])
		vl.commitChanges()
		pt = QgsPointXY()
		fields = vl.fields()
		feature = QgsFeature()
		feature.setFields(fields)
		feature = feature.attributes()
		outFeature = QgsFeature()
		# QgsProject.instance().addMapLayer(vl)
		caps = vl.dataProvider().capabilities()
		# attrs = vl.feature()
		if caps & QgsVectorDataProvider.AddFeatures:
			for feat in nodeLyr.getFeatures():
				# feat = QgsFeature(vl.fields())
				feature[0] = feat.attributes()[0]
				feature[1]= feat.attributes()[1]
				feature[2] = feat.attributes()[5].split(' ')[0]
				# feature[3] = NULL
				pt.setX(float(feat["Coordinates"].split(',')[0]))
				pt.setY(float(feat["Coordinates"].split(',')[1]))
				# pt.setX(float(feat["X"]))
				# pt.setY(float(feat["Y"]))
				outFeature.setGeometry(QgsGeometry.fromPointXY(pt))
				outFeature.setAttributes(feature)
			# outFeature.setGeometry(float(feat["Longitude"]),float(feat["Latitude"]))
				pr.addFeature(outFeature)
				vl.updateExtents()
			# outLayer.addFeature(outFeature)
				# geom = feature.geometry()
				# geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
				# res, outFeats = vl.addFeature(outFeature)
		error_node = QgsVectorFileWriter.writeAsVectorFormat(
			vl, pipes_file, "UTF-8", epsg4326, "ESRI Shapefile")
		# QgsProject.instance().addMapLayer(vl)
		Lyr = QgsVectorLayer(pipes_file, "Nodes", "ogr")
		QgsProject.instance().addMapLayer(Lyr)
		QgsProject.instance().addMapLayer(vl)
		return 
		#setting up reprojection for temporary points
		# epsg4326 = QgsCoordinateReferenceSystem(
		#     4326,
		#     QgsCoordinateReferenceSystem.EpsgCrsId)
		# self.reprojectgeographic = QgsCoordinateTransform(
		#     self.iface.mapCanvas().mapSettings().destinationCrs(),
		#     epsg4326, QgsProject.instance())
		# QgsProject.instance().addMapLayer(pipeLyr)
		# spatRef = QgsCoordinateReferenceSystem(int(Coordinate_Reference_System.split(':')[1]), QgsCoordinateReferenceSystem.EpsgCrsId)
		# spatRef = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
		# QgsProject.instance().addMapLayer(vl)
		# inp_tab = QgsVectorLayer(nodes_file, 'Input_Table', 'ogr')
		# prov = inp_tab.dataProvider()
		# fields = inp_tab.fields()
		# outLayer = QgsVectorLayer(pipes_file, "nodes in zone", "ogr")
 
		# pt = QgsPointXY()
		# outFeature = QgsFeature()
 
		# for feat in inp_tab.getFeatures():
		# 	attrs = feat.attributes()
		# 	pt.setX(float(feat["Coordinates"].split(',')[0]))
		# 	pt.setY(float(feat["Coordinates"].split(',')[1]))
		# 	outFeature.setAttributes(attrs)
		# 	# outFeature.setGeometry(float(feat["Longitude"]),float(feat["Latitude"]))
		# 	outFeature.setGeometry(QgsGeometry.fromPointXY(pt))
		# 	outLayer.addFeature(outFeature)
		# # del outLayer
		# QgsProject.instance().addMapLayer(outLayer)


	def t0_Update_Pipe(self):
		nodes_file = self.dlg.lineEdit_23.text()
		# ogr2ogr.main(["","-f", "ESRI Shapefile", "-s_srs", "epsg:32643", "-t_srs", "epsg:4326", "newp.shp", nodes_file])
		nodeLyr = QgsVectorLayer(nodes_file, "nodes", "ogr")
		pipes_file = self.dlg.lineEdit_24.text()
		# ogr2ogr.main(["","-f", "ESRI Shapefile", "-s_srs", "epsg:32643", "-t_srs", "epsg:4326", "newl.shp", pipes_file])
		# pipeLyr = QgsVectorLayer(pipes_file, "updated pipes", "ogr")
# 		spatialref = osr.SpatialReference()  # Set the spatial ref.
# 		spatialref.SetWellKnownGeogCS('WGS84')  # WGS84 aka ESPG:4326

# 		driver = ogr.GetDriverByName("ESRI Shapefile")
# 		dstfile = driver.CreateDataSource(pipes_file) # Your output file

# # Please note that it will fail if a file with the same name already exists
# 		dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=ogr.wkbLineString) 

# # Add the other attribute fields needed with the following schema :
# 		fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
# 		fielddef.SetWidth(10)
# 		dstlayer.CreateField(fielddef)

# 		fielddef = ogr.FieldDefn("Name", ogr.OFTString)
# 		fielddef.SetWidth(80)
# 		dstlayer.CreateField(fielddef)

# 		fielddef = ogr.FieldDefn("WKT", ogr.OFTString)
# 		fielddef.SetWidth(80)
# 		dstlayer.CreateField(fielddef)


# 		with open(nodes_file) as file_input:
# 			reader = csv.reader(file_input)
# 			next(reader) # Skip the header
# 			for nb, row in enumerate(reader): 
# 		# WKT is in the first field in my test file :
# 				poly = ogr.CreateGeometryFromWkt("LINESTRING(8565997.747151969 3539708.133429219, 8565997.601737406 3539702.196440083, 8565958.586998144 3539703.5234576496)")
# 				feature = ogr.Feature(dstlayer.GetLayerDefn())
# 				feature.SetGeometry(poly)
# 				feature.SetField("ID", nb) # A field with an unique id.
# 				feature.SetField("WKT", row[0])
# 				feature.SetField("Name", row[1])
# 				dstlayer.CreateFeature(feature)
# 			feature.Destroy()
# 			dstfile.Destroy()
# 		# QgsProject.instance().addMapLayer(dstlayer)
# 		return 
		vl = QgsVectorLayer("LineString?crs=epsg:4326", "temporary_points", "memory")
		pr = vl.dataProvider()


		#setting up reprojection for temporary points
		epsg4326 = QgsCoordinateReferenceSystem(
			4326,
			QgsCoordinateReferenceSystem.EpsgCrsId)
		self.reprojectgeographic = QgsCoordinateTransform(
			self.iface.mapCanvas().mapSettings().destinationCrs(),
			epsg4326, QgsProject.instance())
		# Enter editing mode
		vl.startEditing()
		# add fields
		# pr.addAttributes([
		#     QgsField("id", QVariant.Int),
		#     QgsField("pipe_name", QVariant.String),
		#     QgsField("GeoLoc", QVariant.String),
		#     QgsField("Pipe_dia", QVariant.String),
		#     QgsField("type", QVariant.String),
		#     QgsField("typeE", QVariant.String),
		#     QgsField("matA", QVariant.Int),
		#     QgsField("typeB", QVariant.String),
		#     QgsField("matB", QVariant.Int),
		#     QgsField("typeC", QVariant.String),
		#     QgsField("matC", QVariant.Int),
		#     QgsField("matD", QVariant.Int),
		#     QgsField("length", QVariant.Int),
		#     QgsField("endnode", QVariant.Int),
		#     QgsField("startnode", QVariant.String)])
		pr.addAttributes([
			QgsField("Id", QVariant.Int),
			QgsField("Name", QVariant.String),
			QgsField("Length(m)", QVariant.String),
			QgsField("startnode", QVariant.String),
			QgsField("endnode", QVariant.String)])
		vl.commitChanges()
		# pt = QgsPointXY()
		fields = vl.fields()
		feature = QgsFeature()
		feature.setFields(fields)
		feature = feature.attributes()
		outFeature = QgsFeature()
		# QgsProject.instance().addMapLayer(vl)
		caps = vl.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddFeatures:
			for feat in nodeLyr.getFeatures():
				# feat = QgsFeature(vl.fields())
				feature[0] = feat.attributes()[0]
				feature[1]= feat.attributes()[1]
				feature[2] = feat.attributes()[13]
				feature[3] = feat.attributes()[14]
				feature[4] = feat.attributes()[15]


				# attrs = feat.attributes()# pt.setX(float(feat["Longitude"])# pt.setY(float(feat["Latitude"]))
				# poly = ogr.CreateGeometryFromWkt(feat["wkt_str"])# feature = ogr.Feature(dstlayer.GetLayerDefn())
				# outFeature.setGeometry(poly)# wkb = bytes.fromhex((feat["GeoLoc"])[2:]);
				g = QgsGeometry.fromWkt(feat["wkt_str"])
				outFeature.setGeometry(g)
				outFeature.setAttributes(feature)
				# outFeature.setGeometry(float(feat["Longitude"]),float(feat["Latitude"]))
				pr.addFeature(outFeature)
				vl.updateExtents()
				# outLayer.addFeature(outFeature)
				# geom = feature.geometry()
				# geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
				# res, outFeats = vl.addFeature(outFeature)
		
		error_node = QgsVectorFileWriter.writeAsVectorFormat(
			vl, pipes_file, "UTF-8", epsg4326, "ESRI Shapefile")
		Lyr = QgsVectorLayer(pipes_file, "Pipes", "ogr")
		QgsProject.instance().addMapLayer(Lyr)
		# QgsProject.instance().addMapLayer(vl)
		return

		#setting up reprojection for temporary points
		# epsg4326 = QgsCoordinateReferenceSystem(
		#     4326,
		#     QgsCoordinateReferenceSystem.EpsgCrsId)
		# self.reprojectgeographic = QgsCoordinateTransform(
		#     self.iface.mapCanvas().mapSettings().destinationCrs(),
		#     epsg4326, QgsProject.instance())
		# QgsProject.instance().addMapLayer(pipeLyr)
		# spatRef = QgsCoordinateReferenceSystem(int(Coordinate_Reference_System.split(':')[1]), QgsCoordinateReferenceSystem.EpsgCrsId)
		spatRef = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
 
		inp_tab = QgsVectorLayer(pipes_file, 'Input_Table', 'ogr')
		prov = inp_tab.dataProvider()
		fields = inp_tab.fields()
		outLayer = QgsVectorLayer(nodes_file, "pipes in zone", "ogr")
 
		# pt = QgsPointXY()
		g = QgsGeometry()
		outFeature = QgsFeature()
 
		for feat in inp_tab.getFeatures():
			attrs = feat.attributes()

			# wkb = bytes.fromhex((feat["GeoLoc"])[2:]);
			# g.fromWkb(wkb)

			# pt.setX(float(feat["Longitude"]))
			# pt.setY(float(feat["Latitude"]))
			outFeature.setAttributes(attrs)
			# outFeature.setGeometry(float(feat["Longitude"]),float(feat["Latitude"]))
			# outFeature.setGeometry(wkb.loads((feat["GeoLoc"])[2:]))
			outLayer.addFeature(outFeature)
		# del outLayer
		
		QgsProject.instance().addMapLayer(outLayer)






	def run(self):
		"""Run method that performs all the real work"""

		# Create the dialog with elements (after translation) and keep reference
		# Only create GUI ONCE in callback, so that it will only load when the plugin is started
		if self.first_start == True:
			self.first_start = False
			self.dlg = PHEDDialog()
			self.dlg.pushButton_9.clicked.connect(self.t0_Upload_Node_Layer)
			self.dlg.pushButton_10.clicked.connect(self.t1_Upload_Node_Layer)
			self.dlg.pushButton_7.clicked.connect(self.t0_Upload_Pipeline_Layer)
			self.dlg.pushButton_8.clicked.connect(self.t1_Upload_Pipeline_Layer)
			self.dlg.pushButton.clicked.connect(self.t0_Update_Pipeline_Layer)
			self.dlg.pushButton_2.clicked.connect(self.t0_Update_Pipe)
			#zone wise feature selection
		# show the dialog
		self.dlg.show()
		# Run the dialog event loop
		self.dlg.lineEdit_21.clear()
		self.dlg.lineEdit_22.clear()
		self.dlg.lineEdit_23.clear()
		self.dlg.lineEdit_24.clear()
		result = self.dlg.exec_()
		# See if OK was pressed
		if result:
			# Do something useful here - delete the line containing pass and
			# substitute with your code.
			# if result:
			# Do something useful here - delete the line containing pass and
			# substitute with your code.
			self.iface.messageBar().pushMessage("Completed",
												"Completed", level=Qgis.Success, duration=3)

			# pass
