from qgis.core import QgsMapLayer, QgsPointXY, QgsRectangle, QgsWkbTypes
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.PyQt.QtGui import QColor

class multi_selection_rectangle(QgsMapTool):

    def __init__(self, canvas, action, main):
        self.canvas = canvas
        self.main = main
        self.active = False
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        mFillColor = QColor( 254, 178, 76, 63 );
        self.rubberBand.setColor(mFillColor)
        self.rubberBand.setWidth(1)
        self.reset()
    
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
    
    # quand on clique, créé un rectangle avec la position du click
    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)
    
    # quand on relache 
    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        layers = self.canvas.layers()
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                continue
            if r is not None:
                lRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, r)
                layer.selectByRect(lRect, layer.SelectBehavior.SetSelection)
                self.main.selected = 1
        self.rubberBand.hide()
    
    # étends le rectangle jusqu'au curseur
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates( e.pos() )
        self.showRect(self.startPoint, self.endPoint)
    
    # affiche le rectangle pour voir la sélection 
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())
    
        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)    # true pour mettre à jour le canvas
        self.rubberBand.show()
    
    # récupère un réctangle si les points sont valides
    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None
    
        return QgsRectangle(self.startPoint, self.endPoint)
    
    # désactive l'outil
    def deactivate(self):
        self.rubberBand.reset()
        try:
            if self is not None:
                QgsMapTool.deactivate(self)
        except:
            pass
    
    # active l'outil
    def activate(self):
        QgsMapTool.activate(self)

    def unload(self):
        self.deactivate()
    
