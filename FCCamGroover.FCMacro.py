import FreeCAD
#from Macro_3D_Parametric_Curve import ParamCurv
from FreeCAD import Base
from PySide import QtGui,QtCore
import Part, Draft
from math import *
import time
from DraftTools import msg as say


__title__ = "FCBmpImport"
__author__ = "TheMarkster"
__url__ = "https://github.com/mwganson/fccamgroover"
__Wiki__ = "https://github.com/mwganson/fccamgroover/blob/master/README.md"
__date__ = "2018.07.17" #year.month.date and optional a,b,c, etc. subrevision letter, e.g. 2018.10.16a
__version__ = __date__

#OS: Windows 10
#Word size of OS: 64-bit
#Word size of FreeCAD: 64-bit
#Version: 0.18.14061 (Git)
#Build type: Release
#Branch: master
#Hash: c4fc02cbcfff975712e977dc08f859fba71ba0ad
#Python version: 2.7.14
#Qt version: 4.8.7
#Coin version: 4.0.0a
#OCC version: 7.2.0
#Locale: English/UnitedStates (en_US)



msg = u"""FC Cam Groover, a macro to create a cam groove in a cylinder, by 'TheMarkster', 2018, (incorporating code 
from the '3D Parametric Curve Macro' by Gomez Lucio and Laurent Despeyroux, 2015).  Credit also to user emills2 for his 
invaluable feedback.<br/>
<br/>
The cylinder produced will be similar to the one depicted in this video: <a href = 'https://youtu.be/io1JL1U7kUs'>https://youtu.be/io1JL1U7kUs</a><br/>
<br/>
Parameters supported: <br/>
<br/>
cylinder height, <br/>
cylinder radius, <br/>
groove depth, <br/>
groove width, <br/>
strokes per revolution, <br/>
stroke range, <br/>
<br/>

<br/>
Copyright (c) 2018 by 'TheMarkster'<br/>                                                                         
<br/>
This file is a supplement to the FreeCAD CAx development system.      
<br/>
                                                                         
<br/>
This program is free software; you can redistribute it and/or modify  
<br/>
it under the terms of the GNU Lesser General Public License (LGPL)    
<br/>
as published by the Free Software Foundation; either version 2 of     
<br/>
the License, or (at your option) any later version.                   
<br/>
                                                                         
<br/>
This software is distributed in the hope that it will be useful,      
<br/>
but WITHOUT ANY WARRANTY; without even the implied warranty of        
<br/>
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         
<br/>
GNU Library General Public License at <a href='http://www.gnu.org/licenses'>http://www.gnu.org/licenses</a> 
<br/>
for more details.                                                     
<br/>
                                                                         
<br/>
For more information about the GNU Library General Public License     
<br/>
write to the Free Software Foundation, Inc., 59 Temple Place,         
<br/>
Suite 330, Boston, MA  02111-1307 USA                                 
<br/>
                                                                         
<br/>
<br/>

"""
title = u"""Welcome to FC Cam Groover Macro"""
icon=QtGui.QMessageBox.Information
diag = QtGui.QMessageBox(icon, title, msg)
diag.setWindowModality(QtCore.Qt.ApplicationModal)
diag.setTextFormat(QtCore.Qt.RichText); 
diag.exec_()

window = QtGui.QMainWindow()
def processEvents():
     time.sleep(0.001)
     QtGui.QApplication.processEvents()

def getDouble(txt1,txt2,default):
    inp,ok = QtGui.QInputDialog.getDouble(window, txt1,txt2,default, 0,1000000, 1)
    if ok:
        return inp
    else:
        raise StandardError('User canceled')

def getInt(txt1,txt2,default):
    inp, ok = QtGui.QInputDialog.getInt(window, txt1,txt2,default, 1, 100000, 1)
    if ok:
        return inp
    else:
        raise StandardError('User canceled')




#radius=60 # radius of cylinder
#depth=5 #depth of cut (along x/y axis)
#slotHeight = 5 #height of slot (along z-axis)
#innerRadius = radius-depth
#strokeFactor = 1 #length of stroke along axial direction (1 = radius, 2 = 2 * radius, .5 = .5 * radius, etc.)
#cylinderHeight = 100 #length of cylinder
#strokesPerRevolution = 2 #should be an integer 


radius = getDouble(u'Radius of Cylinder',u'Enter radius of cylinder (in mm).  Make sure it\'s big enough or the operation will fail:',10)
cylinderHeight = getDouble(u'Height of Cylinder', u'Enter the height of the cylinder (in mm)  Make sure it\'s tall enough or else the operation will fail:',10)
depth = getDouble(u'Depth of Groove', u'Enter the depth of the groove to be cut into the cylinder (in mm):',2)
slotHeight = getDouble(u'Height of Groove',u'Enter the height of the slot to be cut into the cylinder.  Note: this is not the stroke length, which will be input below. (in mm) ',2)
innerRadius = radius-depth
strokeFactor = getDouble(u'Stroke Length',u'Enter the axial length of the stroke: (in mm)',5)
strokeFactor /= radius
strokesPerRevolution = getInt(u'Strokes per Revolution',u'Enter the number of strokes per revolution of the cylinder:', 2)




### 3d parametric curve source now incorporated directly into the macro in order to save users the fuss of 
### having to install it and then rename it.  Also gives me the chance to fix a little bug that kept giving 
### an exception.

### BEGIN insert of 3d parametric curve macro


# -*- coding: utf-8 -*-
# Create a 3D parametric Curve.
# Author: Gomez Lucio
# Modified by Laurent Despeyroux on 9th feb 2015
#   - 3 helping variables added a, b and c
#   - enlarged GUI
#   - more flexible GUI
#   - basic error mangement
 
#import FreeCAD
#from PySide import QtGui,QtCore
#import Part
#import Draft
#from math import *
 
class ParamCurv(QtGui.QWidget):
    def __init__(self):
        super(ParamCurv, self).__init__()
        self.initUI()
    def initUI(self):
        self.op2 = QtGui.QCheckBox("    Bspline",self) #moved here from below to avoid having it accessed before being initialized -- <TheMarkster>
        self.t0 = QtGui.QLabel("Equation :",self)
        self.ta = QtGui.QLabel("    a(t) ",self)
        self.la = QtGui.QLineEdit(self)
        self.la.setText("37")
        self.tb = QtGui.QLabel("    b(a,t) ",self)
        self.lb = QtGui.QLineEdit(self)
        self.lb.setText("1")
        self.tc = QtGui.QLabel("    c(a,b,t) ",self)
        self.lc = QtGui.QLineEdit(self)
        self.lc.setText("(a+cos(a*t)*2)*b")
        self.t1 = QtGui.QLabel("    X(a,b,c,t) ",self)
        self.l1 = QtGui.QLineEdit(self)
        self.l1.setText("cos(t)*c")
        self.t2 = QtGui.QLabel("    Y(a,b,c,t) ",self)
        self.l2 = QtGui.QLineEdit(self)
        self.l2.setText("sin(t)*c")
        self.t3 = QtGui.QLabel("    Z(a,b,c,t) ",self)
        self.l3 = QtGui.QLineEdit(self)
        self.l3.setText("0")
        self.t31 = QtGui.QLabel("Parameters :",self)
        self.t4 = QtGui.QLabel("    Min t ",self)
        self.l4 = QtGui.QLineEdit(self)
        self.l4.setText("0")
        self.t5 = QtGui.QLabel("    Max t ",self)
        self.l5 = QtGui.QLineEdit(self)
        self.l5.setText("6.283185")
        self.t6 = QtGui.QLabel("    Interval ",self)
        self.l6 = QtGui.QLineEdit(self)
        self.l6.setText("0.01")
        self.t7 = QtGui.QLabel("Type of Line :",self)
        self.op1 = QtGui.QCheckBox("    Polyline",self)
        self.poly = False
        self.op1.stateChanged.connect(self.polyState)
        self.op1.setCheckState(QtCore.Qt.Checked)

        self.bsline = False
        self.op2.stateChanged.connect(self.bsplineState)
        self.t8 = QtGui.QLabel("    Closed Curve",self)
        self.op3 = QtGui.QCheckBox("",self)
        self.cclose = False
        self.op3.stateChanged.connect(self.ccloseState)
        self.createbutt = QtGui.QPushButton("Create Curve",self)
        self.exitbutt = QtGui.QPushButton("Close",self)
        layout = QtGui.QGridLayout()
        self.resize(420, 380)
        self.setWindowTitle("Parametric Curve ")
        i = 0
        layout.addWidget(self.t0, i, 0)
        i = i+1
        layout.addWidget(self.ta, i, 0)
        layout.addWidget(self.la, i, 1)
        i = i+1
        layout.addWidget(self.tb, i, 0)
        layout.addWidget(self.lb, i, 1)
        i = i+1
        layout.addWidget(self.tc, i, 0)
        layout.addWidget(self.lc, i, 1)
        i = i+1
        layout.addWidget(self.t1, i, 0)
        layout.addWidget(self.l1, i, 1)
        i = i+1
        layout.addWidget(self.t2, i, 0)
        layout.addWidget(self.l2, i, 1)
        i = i+1
        layout.addWidget(self.t3, i, 0)
        layout.addWidget(self.l3, i, 1)
        i = i+1
        layout.addWidget(self.t31, i, 0)
        i = i+1
        layout.addWidget(self.t4, i, 0)
        layout.addWidget(self.l4, i, 1)
        i = i+1
        layout.addWidget(self.t5, i, 0)
        layout.addWidget(self.l5, i, 1)
        i = i+1
        layout.addWidget(self.t6, i, 0)
        layout.addWidget(self.l6, i, 1)
        i = i+1
        layout.addWidget(self.t8, i, 0)
        layout.addWidget(self.op3, i, 1)
        i = i+1
        layout.addWidget(self.t7, i, 0)
        i = i+1
        layout.addWidget(self.op1, i, 0)
        layout.addWidget(self.op2, i, 1)
        i = i+1
        layout.addWidget(self.createbutt, i, 0)
        layout.addWidget(self.exitbutt, i, 1)
        self.setLayout(layout)
        #self.show() #--no need to show this gui -- <TheMarkster>
        QtCore.QObject.connect(self.createbutt, QtCore.SIGNAL("pressed()"),self.draw)
        QtCore.QObject.connect(self.exitbutt, QtCore.SIGNAL("pressed()"),self.close)
    def ccloseState(self, state):
        if state == QtCore.Qt.Checked:
            self.cclose = True
        else:
            self.cclose = False
    def bsplineState(self, state):
        if state == QtCore.Qt.Checked:
            self.bsline = True
            self.op1.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.bsline = False
    def polyState(self, state):
        if state == QtCore.Qt.Checked:
            self.poly = True
            self.op2.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.poly = False
    def draw(self):
        msgBox = QtGui.QMessageBox()
        fa = str(self.la.text())
        fb = str(self.lb.text())
        fc = str(self.lc.text())
        fx = str(self.l1.text())
        fy = str(self.l2.text())
        fz = str(self.l3.text())
        t = float(str(self.l4.text()))
        tf = float(self.l5.text())
        intv = float(str(self.l6.text()))
        d=(tf-t)/intv
        matriz = []

        for i in range(int(d)):
            say('Processing '+str(i)+' of '+ str(d)+'\n') #added by TheMarkster
            processEvents() #added by TheMarkster
            try:
              value="a"
              a=eval(fa)
              value="b"
              b=eval(fb)
              value="c"
              c=eval(fc)
              value="X"
              fxx=eval(fx)
              value="Y"
              fyy=eval(fy)
              value="Z"
              fzz=eval(fz)
            except ZeroDivisionError:
              msgBox.setText("Error division by zero in calculus of "+value+"() for t="+str(t)+" !")
              msgBox.exec_()
            except:
              msgBox.setText("Error in the formula of "+value+"() !")
              msgBox.exec_()
            matriz.append(FreeCAD.Vector(fxx,fyy,fzz))
            t+=intv
        curva = Part.makePolygon(matriz)
        if self.bsline == True:
            Draft.makeBSpline(curva,closed=self.cclose,face=False)
        if self.poly == True:
            Draft.makeWire(curva,closed=self.cclose,face=False)
    def close(self):
        self.hide()
 
#ParamCurv()  #--we'll initialize it ourselves below -- <TheMarkster>

### END OF 3d parametric curve macro source





par = ParamCurv()
par.hide()
par.la.setText(str(strokesPerRevolution)) #a
par.lb.setText(str(strokeFactor)) #b
par.lc.setText(str(radius)) #c
par.cclose=True #make closed bspline
par.bsline = True #make bspline
par.poly=False #don't make dwire
par.l3.setText('cos(t*a/2)*sin(t*a/2)*c*b') #z

if not App.ActiveDocument:
    App.newDocument()
say(u'Making bspline #1...\n')
processEvents()
par.draw() #BSpline
say(u'Making bspline #2...\n')
processEvents()
par.draw() #BSpline001
#par.lc.setText(str(innerRadius)) #try using draft scale to make the larger radius bsplines, only don't scale in z-direction
#par.draw() #BSpline002
#par.draw() #BSpline003
say(u'Scaling bspline1...\n')
processEvents()
Draft.scale([FreeCAD.ActiveDocument.BSpline],delta=FreeCAD.Vector(innerRadius/float(radius),innerRadius/float(radius),1.0),center=FreeCAD.Vector(0.0,0.0,0.0),copy=True,legacy=True)
say(u'Scaling bspline2...\n')
processEvents()
Draft.scale([FreeCAD.ActiveDocument.BSpline],delta=FreeCAD.Vector(innerRadius/float(radius),innerRadius/float(radius),1.0),center=FreeCAD.Vector(0.0,0.0,0.0),copy=True,legacy=True)
say(u'Placing bsplines...\n')
processEvents()
App.ActiveDocument.BSpline001.Placement=App.Placement(App.Vector(0,0,slotHeight), App.Rotation(0,0,0), App.Vector(0,0,0))
App.ActiveDocument.BSpline003.Placement=App.Placement(App.Vector(0,0,slotHeight), App.Rotation(0,0,0), App.Vector(0,0,0))
say(u'Making ruled surfaces...\n')
processEvents()
FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
FreeCAD.ActiveDocument.ActiveObject.Curve1=(FreeCAD.ActiveDocument.BSpline001,['Edge1'])
FreeCAD.ActiveDocument.ActiveObject.Curve2=(FreeCAD.ActiveDocument.BSpline003,['Edge1'])
FreeCAD.ActiveDocument.getObject("Ruled_Surface").Orientation = u"Forward"

FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
FreeCAD.ActiveDocument.ActiveObject.Curve1=(FreeCAD.ActiveDocument.BSpline002,['Edge1'])
FreeCAD.ActiveDocument.ActiveObject.Curve2=(FreeCAD.ActiveDocument.BSpline003,['Edge1'])

FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
FreeCAD.ActiveDocument.ActiveObject.Curve1=(FreeCAD.ActiveDocument.Ruled_Surface,['Edge1'])
FreeCAD.ActiveDocument.ActiveObject.Curve2=(FreeCAD.ActiveDocument.BSpline,['Edge1'])

FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
FreeCAD.ActiveDocument.ActiveObject.Curve1=(FreeCAD.ActiveDocument.Ruled_Surface002,['Edge3'])
FreeCAD.ActiveDocument.ActiveObject.Curve2=(FreeCAD.ActiveDocument.Ruled_Surface001,['Edge1'])
FreeCAD.ActiveDocument.getObject("Ruled_Surface003").Orientation = u"Reversed"

Gui.activeDocument().getObject("BSpline").Visibility=False
Gui.activeDocument().getObject("BSpline001").Visibility=False
Gui.activeDocument().getObject("BSpline002").Visibility=False
Gui.activeDocument().getObject("BSpline003").Visibility=False

App.ActiveDocument.recompute()

say(u'Building shell...\n')
processEvents()

_=Part.Shell([App.ActiveDocument.Ruled_Surface003.Shape.Face1, App.ActiveDocument.Ruled_Surface002.Shape.Face1, App.ActiveDocument.Ruled_Surface.Shape.Face1, App.ActiveDocument.Ruled_Surface001.Shape.Face1, ])
if _.isNull(): raise RuntimeError('Failed to create shell')
App.ActiveDocument.addObject('Part::Feature','Shell').Shape=_.removeSplitter()
del _

Gui.activeDocument().getObject("Ruled_Surface").Visibility=False
Gui.activeDocument().getObject("Ruled_Surface002").Visibility=False
Gui.activeDocument().getObject("Ruled_Surface001").Visibility=False
Gui.activeDocument().getObject("Ruled_Surface003").Visibility=False

Gui.activeDocument().getObject("Shell").Visibility=False

App.ActiveDocument.recompute()

say(u'Making shell into a solid...\n')
processEvents()

__s__=App.ActiveDocument.Shell.Shape
__s__=Part.Solid(__s__)
__o__=App.ActiveDocument.addObject("Part::Feature","Shell_solid")
__o__.Label="Shell (Solid)"
__o__.Shape=__s__
del __s__, __o__

App.ActiveDocument.recompute()

say('Building cylinder...\n')
processEvents()
App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
App.ActiveDocument.ActiveObject.Label = "Cylinder"
App.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")
App.ActiveDocument.getObject("Cylinder").Radius = str(radius)
App.ActiveDocument.getObject("Cylinder").Height = str(cylinderHeight)
App.ActiveDocument.Cylinder.Placement=App.Placement(App.Vector(0,0,-1.0*cylinderHeight/2.0), App.Rotation(0,0,0), App.Vector(0,0,0))


App.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")

msg=u'Done.  Last thing you need to do is the boolean cut from the Part workbench, cutting Shell (Solid) from the cylinder, if all looks good.\n'
title=u'Thanks for using FC Cam Groover'
icon=QtGui.QMessageBox.Information
diag = QtGui.QMessageBox(icon, title, msg)
diag.setWindowModality(QtCore.Qt.ApplicationModal)
diag.setTextFormat(QtCore.Qt.RichText); 
diag.exec_()


#App.activeDocument().addObject("Part::Cut","Cut")
#App.activeDocument().Cut.Base = App.activeDocument().Cylinder
#App.activeDocument().Cut.Tool = App.activeDocument().Shell_solid
#Gui.activeDocument().Cylinder.Visibility=False
#Gui.activeDocument().Shell_solid.Visibility=False

