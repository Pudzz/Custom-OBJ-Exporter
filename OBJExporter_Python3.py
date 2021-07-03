import pymel.core as pm
import sys
from PySide2 import QtCore, QtWidgets

#------ GUI ------#

guiWindow = QtWidgets.QWidget()
guiWindow.resize(300,200)
guiWindow.setWindowTitle("OBJ Exporter")

mainLayout = QtWidgets.QVBoxLayout(guiWindow)

browserText = QtWidgets.QLabel("Filename ")
textLine = QtWidgets.QLineEdit()
browseButton = QtWidgets.QPushButton("Browse")

browserLayout = QtWidgets.QHBoxLayout()
mainLayout.addLayout(browserLayout)

browserLayout.addWidget(browserText)
browserLayout.addWidget(textLine)
browserLayout.addWidget(browseButton)

groupBox = QtWidgets.QGroupBox("Basic options")

basicOptionLayout = QtWidgets.QVBoxLayout()
groupBox.setLayout(basicOptionLayout)    

mainLayout.addWidget(groupBox)    

trangulateBox = QtWidgets.QCheckBox("Triangulate")
exportSelectionBox = QtWidgets.QCheckBox("Export selection")
exportMaterialBox = QtWidgets.QCheckBox("Export material")

basicOptionLayout.addWidget(trangulateBox)
basicOptionLayout.addWidget(exportSelectionBox)
basicOptionLayout.addWidget(exportMaterialBox)

radioText = QtWidgets.QLabel("Space:")
localRadio = QtWidgets.QRadioButton("Local")
globalRadio = QtWidgets.QRadioButton("Global")
localRadio.setChecked(True)

radioOptionsLayout = QtWidgets.QHBoxLayout()
basicOptionLayout.addLayout(radioOptionsLayout)

radioOptionsLayout.addWidget(radioText)
radioOptionsLayout.addWidget(localRadio)
radioOptionsLayout.addWidget(globalRadio)

exportButton = QtWidgets.QPushButton("Export")
closeButton = QtWidgets.QPushButton("Close")

buttonsLayout = QtWidgets.QHBoxLayout()
mainLayout.addLayout(buttonsLayout)

buttonsLayout.addWidget(exportButton)
buttonsLayout.addWidget(closeButton)

guiWindow.show()

# - - CODE - - #

# Type a path where the OBJ is created
def savePath():
    mySave = pm.fileDialog2(startingDirectory = "C:", fileFilter = "Obj (*.obj)", dialogStyle = 2, caption = "Obj Exporter")
    textLine.setText(mySave[0])

# Export .OBJ function
def export():
    
    totalPos = 1
    totalUVs = 1
    totalNormals = 1
    
    materialIndex = 0
    
    if exportSelectionBox.isChecked() == False:
        pm.select(all = True)
        
    if textLine.text() == "":
        savePath()
        
    if localRadio.isChecked() == True:
        radioButtonText = "object"
    else:
        radioButtonText = "world"
        
    # Open file and handle info for material and object
    filePath = textLine.text()
    with open(filePath, 'w') as objfile:        
    
        if exportMaterialBox.isChecked() == True:
            mtlFileName = (str(filePath[:filePath.rfind(".")]) + ".mtl")
            
            with open(mtlFileName, 'w') as mtl:
                
                materialList = []
                
                for mtlobject in pm.ls(sl = True, type = "transform"):
                    mtlobjShape = mtlobject.getShape()
                    print(mtlobjShape)
                    shadingGroup = mtlobjShape.listConnections(type = "shadingEngine")
                    print(shadingGroup)
                    objMat = shadingGroup[0]    
                    print(objMat)
                    objMaterial = objMat.listConnections(source = True, destination = False)[0]
                    print(objMaterial)    
                    materialList.append(objMat)
                    print(materialList)
                    matInfo = objMat.listConnections(type = "materialInfo")
                    print(matInfo)
                    materialInfo = matInfo[0]
                    print(materialInfo)
                    fileNode = materialInfo.listConnections(type = 'file')
                    print(fileNode)
                    
                    # If there is a texture
                    if fileNode != []:
                        textureFile = pm.getAttr(fileNode[0].fileTextureName) 
                        
                        pm.sysFile(textureFile, copy = str(filePath[:filePath.rfind("/") +1] + str(textureFile[textureFile.rfind("/") +1:])))                        
                        mtlFileName = str(textureFile[textureFile.rfind("/") +1:])
                        print(mtlFileName)  
                    
                             
                    mtl.write("newmtl " + objMat + "\n")  
                    
                    # Different material lightning and shadoweffects [Hardcoded 4] 
                    mtl.write("illum 4\n")    
                    
                    # Diffuse color
                    matColor = objMaterial.getColor()
                    mtl.write("Kd " + str(matColor[0]) + " " + str(matColor[1]) + " " + str(matColor[2]) + "\n")
                    
                    # Ambient color
                    matAmbient = objMaterial.getAmbientColor()
                    mtl.write("Ka " + str(matAmbient[0]) + " " + str(matAmbient[1]) + " " + str(matAmbient[2]) + "\n")
    
                    # Transparency
                    matTrans = objMaterial.getTransparency()
                    matTrans0 = 1.0 - matTrans[0]
                    matTrans1 = 1.0 - matTrans[1]
                    matTrans2 = 1.0 - matTrans[2]            
                    mtl.write("Tf " + str(matTrans0) + " " + str(matTrans1) + " " + str(matTrans2) + "\n")        
                    
                    # Filepath to texture, if there is one
                    if fileNode != []:
                        mtl.write("map_Kd " + mtlFileName + "\n")
    
                    # Optic density for surface 
                    matRefractive = objMaterial.getRefractiveIndex()
                    mtl.write("Ni " + str(matRefractive) + "\n")
                    
                    # If anything without lambert, get specular color
                    if objMaterial.type() != "lambert":
                        matSpecular = objMaterial.getSpecularColor()
                        mtl.write("Ks " + str(matSpecular[0]) + " " + str(matSpecular[1]) + " " + str(matSpecular[2]) + "\n")        
                                    
                mtl.close()
                
        if (exportMaterialBox.isChecked() == True):
            mtllibName = str(filePath[filePath.rfind("/") +1:])   
            print(mtllibName)
            mtllibName = mtllibName[:mtllibName.rfind(".")]   
            print(mtllibName) 
            objfile.write("mtllib " + mtllibName + ".mtl\n")    
                
        for obj in pm.ls(sl=True, type = 'transform'):
            print(obj)
            
            if (trangulateBox.isChecked() == True):
                temp = pm.duplicate(obj)
                objDup = temp[0]
                pm.polyTriangulate(objDup)
                
                shapeDup = objDup.getShape()
                
                U,V = shapeDup.getUVs()
                UVs = zip(U, V)
                
                objfile.write("g default")
                
                for index, vertex in enumerate(objDup.vtx):
                    objfile.write("\nv")
                    for pos in vertex.getPosition(space = radioButtonText):
                        objfile.write(" ")
                        objfile.write((str(round(pos, 6))))
                        
                for uvs in UVs:
                    objfile.write("\nvt ")
                    objfile.write(str(uvs[0])+" "+str(uvs[1]))                    
                
                for normal in objDup.getNormals():          
                    objfile.write("\nvn ")
                    objfile.write(str(normal[0])+" "+str(normal[1])+" "+str(normal[2]))

                objfile.write("\ns off")    
                objfile.write("\ng ")
                objfile.write(str(obj))
                
                if (exportMaterialBox.isChecked() == True):
                    objfile.write("\nusemtl " +  materialList[materialIndex])
                    materialIndex +=1  
                    
                for index, face in enumerate(objDup.faces):
                    one_face = '\nf'
                    for findex, facevertex in enumerate(face.getVertices()):
                        one_face += ' %s/%s/%s' %(facevertex + totalPos, face.getUVIndex(findex) + totalUVs, face.normalIndex(findex) + totalNormals)
                    objfile.write(one_face)
                
                objfile.write("\n")
                                
                totalPos += len(objDup.vtx)
                uv_data_list = list(UVs)
                totalUVs = len(uv_data_list)       
                totalNormals += len(objDup.getNormals())
                
                pm.delete(objDup)
                
            if(trangulateBox.isChecked() == False):                            
                shape = obj.getShape()   
                U,V = shape.getUVs()                  
                UVs = zip(U, V)  
                
                objfile.write("g default")           
            
                for index, vertex in enumerate(obj.vtx):
                    objfile.write("\nv")    
                    for pos in vertex.getPosition(space = radioButtonText): 
                        objfile.write(" ")
                        objfile.write((str(round(pos, 6))))            
            
                for uvs in UVs:
                    objfile.write("\nvt ")
                    objfile.write(str(uvs[0])+" "+str(uvs[1]))            
                
                for normal in obj.getNormals():            
                    objfile.write("\nvn ")
                    objfile.write(str(normal[0])+" "+str(normal[1])+" "+str(normal[2]))            
               
                objfile.write("\ns off")    
                objfile.write("\ng ")
                objfile.write(str(obj)) 
                
                if (exportMaterialBox.isChecked() == True):
                    objfile.write("\nusemtl " + materialList[materialIndex])
                    materialIndex +=1
                    
                for index, face in enumerate(obj.faces):
                    one_face = '\nf'
                    for findex, facevertex in enumerate(face.getVertices()):
                        one_face += ' %s/%s/%s' %(facevertex + totalPos, face.getUVIndex(findex) + totalUVs, face.normalIndex(findex) + totalNormals)
                    objfile.write(one_face)
                    
                objfile.write("\n")
                totalPos += len(objDup.vtx)
                uv_data_list = list(UVs)
                totalUVs = len(uv_data_list)       
                totalNormals += len(objDup.getNormals())
                
        fileOBJ.close() 

def closeWidget():
    return guiWindow.close()

closeButton.clicked.connect(closeWidget)
exportButton.clicked.connect(export)
browseButton.clicked.connect(savePath)



