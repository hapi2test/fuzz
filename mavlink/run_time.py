
class runTime:
    def __init__(self,mission_list,config_dict,score_list):
        self.mission_list = mission_list
        self.config_dict = config_dict
        self.score_list = score_list


    def get_mission_list(self):
        for mission in self.mission_list:
            print(mission)
    def get_config_dict(self):
        for key in self.config_dict.items():
            print(key)

    def get_score_list_print(self):
        print(f"UAV status: deviation score {self.score_list[0]}, rapid score {self.score_list[1]}, interruption {self.score_list[2]}")
    def get_score(self):
        return self.score_list
    def set_score(self,score_deviation, score_rapi, score_interruption):
        self.score_list = [score_deviation, score_rapi, score_interruption]
