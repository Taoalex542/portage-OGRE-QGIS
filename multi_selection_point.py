from qgis.core import QgsRectangle, QgsMapLayer
from qgis.gui import QgsMapTool

class multi_selection_point(QgsMapTool):

    def __init__(self, canvas, action, main):
        self.canvas = canvas
        self.main = main
        self.active = False
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
    
    # quand on clique sur le canvas, sélectionne tout ce qui est dans le point
    def canvasPressEvent(self, e):
        p = self.toMapCoordinates(e.pos())
        layers = self.canvas.layers()
        w = self.canvas.mapUnitsPerPixel() * 3
        rect = QgsRectangle(p.x()-w, p.y()-w, p.x()+w, p.y()+w)
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                continue
            lRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, rect)
            layer.selectByRect(lRect, layer.SelectBehavior.SetSelection)
    
    # pour activer
    def deactivate(self):
        try:
            if self is not None:
                QgsMapTool.deactivate(self)
        except:
            pass
    
    # pour désactiver
    def activate(self):
        QgsMapTool.activate(self)
        try:
            self.selectionButton.setDefaultAction(self.sender())
        except:
            pass

    # pour décharger
    def unload(self):
        self.deactivate()        
    
