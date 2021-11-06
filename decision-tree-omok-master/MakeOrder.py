import TreeParser
import numpy as np

class MakeOrder:
    def __init__(self):
        pass

    def getnextmap(self,conn,idNum,decision_tree,num_next_map):
        max_winchance = 0
        max_totalcount = 0
        label_max_map = 0
        cur = conn.cursor()
        for i in range(num_next_map):
            # print(type(decision_tree))
            exec(decision_tree,globals())
            result = tree(i)
            # print(result)

            winchance= result[1]/(result[0]+result[1])
            totalcount = result[0]+result[1]
            if winchance >= max_winchance:
                if totalcount > max_totalcount:
                    max_winchance = winchance
                    max_totalcount = totalcount
                    label_max_map = i

        get_map_from_label_sql = """SELECT next_map FROM sampleomok.map_label WHERE idNum = {} AND label = {}"""
        cur.execute(get_map_from_label_sql.format(idNum,label_max_map))
        row = cur.fetchone()
        max_map = row['next_map']

        return {'next_map':max_map,'win_chance':max_winchance}




    def chooseDecisionTree(self,conn,sitRepTurn):
        cur = conn.cursor()
        sel_dt_sql = """SELECT idNum,decision_tree FROM sampleomok.decision_trees WHERE sit_map = '{0}' """
        cur.execute(sel_dt_sql.format(sitRepTurn.m_map))
        row= cur.fetchone()
        if row is not None:
            print("This was not in my train")
            decision_tree = row['decision_tree']
            idNum = row['idNum']
            return idNum, decision_tree
        else:
            return False


    # def findNextMove(self,max_map,sitRepTurn):
    #     # find diff between sitRepTurn.m_map and max_map
    #     # and return position of next moves.
    def stringToArray(self,str_map):
        counter = 0
        array_map = []
        for row in str_map.split('], ['):
            # ugly for now
            if row[:2] == "[[":
                row = row[2:]
            array_map.append(np.fromstring(row, dtype=int, sep=', '))
            # print(np.fromstring(row,dtype=int, sep= ','))

        for row in array_map:
            for cell in row:
                counter+=1 if cell != 0 else 0

        return array_map
    def findDiffInATurn(self,map_before,map_after):
        # map_before , map_after 를 np array로 바꾸자.
        if type(map_before) is str:
            array_map_before = self.stringToArray(map_before)
        else:
            array_map_before = map_before
        array_map_after = self.stringToArray(map_after)

        diff_pos= []
        for y in range(len(array_map_before)):
            for x in range(len(array_map_before[0])):
                if array_map_before[y][x] != array_map_after[y][x]:
                    diff_pos.append({'x':x,'y':y})
        if len(diff_pos)>=2:
            print('something goes wrong, more than 1 turn changed')


        return diff_pos[0]

if __name__ == '__main__':
    mo = MakeOrder()
    decision_tree_str = """
def tree(m_map):
  if m_map <= 0.5:
    return [0.0, 3.0]
  else:  # if m_map > 0.5
    if m_map <= 2.5:
      if m_map <= 1.5:
        return [3.0, 2.0]
      else:  # if m_map > 1.5
        return [2.0, 1.0]
    else:  # if m_map > 2.5
      if m_map <= 3.5:
        return [5.0, 0.0]
      else:  # if m_map > 3.5
        return [2.0, 1.0]
 """
    map_before ='[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 2, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]'
    map_after ='[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 2, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]'

    print(mo.findDiffInATurn(map_before,map_after))