from openpyxl import load_workbook
from .file import *
from .template import *

class Adapter:

    def __init__(self, wb):
        self.wb = wb

    def getRowByDistribution(self, distribution):
        """retourne le numero de la ligne qui contient la distribution"""
        list = []
        Onglet_vlan = self.wb['Vlans']
        for cellule in Onglet_vlan['A']:
            if cellule.value == distribution:
                list.append(cellule.row)
        return list

    def getAccessVlanVar(self, row):
        """retourne les variables d'un vlan d'acces"""
        Onglet_vlan = self.wb['Vlans']
        return { "name": "31 - Ajt Vlan (Member X) - Access.txt",
                "sub_templates" : True,
                "variables" : {
                    "${VLAN_NAME}" : Onglet_vlan['D'+str(row)].value,
                    "${VLAN_ID}" : Onglet_vlan['E'+str(row)].value,
                    "${DESCRIPTION}" : Onglet_vlan['F'+str(row)].value
                    }
                } 
    
    def getDistributionVlanVarInet(self, row):
        """retourne les variables d'un vlan de distribution"""
        Onglet_vlan = self.wb['Vlans']
        Onglet_DHCP = self.wb['Relay-Group DHCP']
        return { "name": "31 - Ajt Vlan (Member X) - Dist.txt",
                "sub_templates" : True,
                "variables" : {
                    "${VLAN_ID}" : Onglet_vlan['E'+str(row)].value,
                    "${DESCRIPTION}" : Onglet_vlan['F'+str(row)].value
                    }
                }
    


    def getDistributionList(self):
        """retourne la liste des distributions"""
        Onglet_vlan = self.wb['Vlans']
        distribution_list = []
        for cell in Onglet_vlan['A']:
            if cell.value != None and cell.value != "Distribution" and cell.value not in distribution_list :
                distribution_list.append(cell.value)
        return distribution_list


