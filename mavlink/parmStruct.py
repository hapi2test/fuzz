
class ParmS:
    def __init__(self, parmName,valueList):
        self.parmName = parmName
        self.valueList = valueList
    def get_value(self,num):
        dict = {
            self.parmName:self.valueList[num]
        }
        return dict
    def get_num(self):
        return len(self.valueList)

