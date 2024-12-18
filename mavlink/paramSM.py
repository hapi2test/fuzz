

class paramSMulti:
    def __init__(self,paramTarget,paramDep,targetValueList,depValueList):
        self.paramTarget = paramTarget
        self.paramDep = paramDep
        self.targetValueList = targetValueList
        self.depValueList = depValueList

    def get_dict(self,num):
        dict = {
            self.paramTarget:self.targetValueList[num],
            self.paramDep:self.depValueList[num]
        }
        return dict

    def get_num(self):
        return len(self.targetValueList)
