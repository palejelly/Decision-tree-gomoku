import pymysql
import json
import MakeOrder

class AIServer(object):
    def __init__(self):

        self.con = pymysql.connect(host='localhost',
                                   user='ddwge',
                                   password= 'ddwge76',
                                   db='ddwge',
                                   cursorclass=pymysql.cursors.DictCursor
                                   )
        self.cur = self.con.cursor()
        self.mo = MakeOrder.MakeOrder()
        print("connection successed")
    def completenessCheck(self):
        latestGame= self.getLatestGame()
        checkRepTurnSql = """SELECT count(*) FROM sampleomok.sit_rep_turn WHERE idGame ={0}""".format(latestGame)

        self.cur.execute(checkRepTurnSql)

        if self.cur.fetchone()  == 0:
            deleteSql="""DELETE
            FROM sampleomok.sit_rep_turn
            WHERE idGame = {0}""".format(latestGame)
            self.cur.execute(deleteSql)
            self.con.commit()
            print("completeness error found")

    def storeSitRep(self,sitRepTurn):

        insertSql="""INSERT INTO sampleomok.sit_rep_turn(idGame,idTurn,type,m_map) VALUES ({0},{1},{2},'{3}')"""

        dumpMap=json.dumps(sitRepTurn.m_map)
        # print(insertSql.format(sitRepTurn.idGame,sitRepTurn.idTurn,dumpMap))
        print(sitRepTurn.idGame,sitRepTurn.idTurn)

        try:
            self.cur.execute(insertSql.format(sitRepTurn.idGame,sitRepTurn.idTurn,sitRepTurn.type,dumpMap))
        except:
            selectSql = """SELECT * FROM sampleomok.sit_rep_turn WHERE idGame = {0} and idTurn ={1}"""
            self.cur.execute(selectSql.format(sitRepTurn.idGame,sitRepTurn.idTurn))
        self.con.commit()

    def storeSitRepGame(self,sitRepGame):
        insertSql="""INSERT INTO sampleomok.sit_rep_game(idGame,gameResult) VALUES ({0},'{1}')"""

        self.cur.execute(insertSql.format(sitRepGame.idGame,sitRepGame.gameResult))
        self.con.commit()

    def getLatestGame(self):
        MaxIdGameSql="""SELECT MAX(idGame) as maxNum FROM sampleomok.sit_rep_game"""
        maxGameNum = 0
        self.cur.execute(MaxIdGameSql)

        maxGameNum = self.cur.fetchone()['maxNum']

        if maxGameNum == None:
            return 1
        else:
            return maxGameNum+1



    def giveNextMove(self,sitRepTurn):
        next_x,next_y = -1,-1
        dt_combined = self.mo.chooseDecisionTree(self.con,sitRepTurn)
        if dt_combined is False:
            return False
        else:
            dt = dt_combined[1]
        self.cur.execute("""SELECT idNum,num_next_map FROM sampleomok.decision_trees WHERE sit_map = '{0}' """.format(sitRepTurn.m_map))
        row = self.cur.fetchone()
        num_next_map = row['num_next_map']
        idNum = row['idNum']
        order = self.mo.getnextmap(self.con,idNum,dt,num_next_map)
        next_map = order['next_map']
        win_chance = order['win_chance']

        next = self.mo.findDiffInATurn(sitRepTurn.m_map,next_map)
        return next,win_chance
        # 승률도 리턴해주면 좋을듯

def main(): # demo use only
    aiserver = AIServer()
    import SitRepTurn
    m_map = '[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 2, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]'
    # m_map 같은 상황이다! 나는 Type 1(1번돌인데) 어디다 두어야할까?
    sitrepTurn= SitRepTurn.SitRepTurn(1,4,m_map,2)
    # 리포트를 만들고,

    next_order = aiserver.giveNextMove(sitrepTurn)
    print(next_order)
    # 서버에 보내서 다음에 뭐할지 받아온다.


if __name__ == '__main__':
    print("start")
    main()