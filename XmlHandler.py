import xml.etree.ElementTree as ET

class XmlHandler:

    def __init__(self,path):
        self._path = path
        with open(path,'a+') as f:
            try:
                self._tree = ET.parse(path)           #Se parsea el XML
                self._root = self._tree.getroot()
                self._i = 2
            except:
                self._tree = self.generate_xml(path)       #Si no existe se genera el formato XML (archivo virgen)
                self._i = 1                         
            
# ---------------------------------------------------------------------------
#Genera formato XML
# ---------------------------------------------------------------------------
    def generate_xml(self,path):
        self._root = ET.Element('cm_models')
        self._root.tail = "\n"                      
        self._root.text = "\n\t"
        tree = ET.ElementTree(self._root)
        tree.write(path)
        return tree
    
# ---------------------------------------------------------------------------
#Append de la nueva entrada 
# ---------------------------------------------------------------------------
    def file_append(self,data):
        cm_model = ET.Element('cm_model')
        cm_model.tail = '\n'                    #formateo del XML <tag>'text'</tag>'tail'
        cm_model.text = '\n\t\t'
        self._root.append(cm_model)
    # <vendor></vendor>
        vendor = ET.SubElement(cm_model,'vendor')
        vendor.text = data['VENDOR']
        vendor.tail = '\n\t\t'
    # <model></model>
        model = ET.SubElement(cm_model,'model')
        model.text=data['MODEL']
        model.tail = '\n\t\t'
    # <softversion></softversion>
        separators = ['\n','\n\t']
        softversion = ET.SubElement(cm_model,'softversion')
        softversion.text=data['SW_REV']
        softversion.tail = '\n\t'
        self._root[-self._i].tail = separators[self._i-1]         #Si es la primer entrada accedemos a root[-1] ya que no existe aun root[-2]
        self._tree.write(self._path)
        print(f'CM listado exitosamente en el archivo "{self._path}" ')

# ---------------------------------------------------------------------------
#Chequea que no exista la entrada
# ---------------------------------------------------------------------------
    def search_file(self,data):
        for cm in self._root.findall('cm_model'):
            compare_dict = {}
            compare_dict['VENDOR'] = cm.find('vendor').text
            compare_dict['MODEL'] = cm.find('model').text
            compare_dict['SW_REV'] = cm.find('softversion').text
            if compare_dict == data:
                print('Este CM ya esta listado en el inventario del archivo, no se permiten entradas duplciadas')
                return(True) 
        return(False)
