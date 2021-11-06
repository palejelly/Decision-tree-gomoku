import pymysql
from pymysql.cursors import DictCursor
import os
import pandas as pd
from sklearn import tree
from sklearn import preprocessing
import numpy as np
import TreeParser

class DrawTree():
    def __init__(self):
        os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
        self.cnx_data = pymysql.connect(host='localhost', port=3306, user='ddwge', passwd='ddwge76', db='ddwge', charset='utf8')
        self.cur_raw = self.cnx_data.cursor(DictCursor)
        self.tree_id = 0
    def iterMaps(self):
        distinct_map_sql = """SELECT Distinct(m_map) FROM sampleomok.sit_rep_turn where type=2"""
        self.cur_raw.execute(distinct_map_sql)
        rows = self.cur_raw.fetchall()

        for row in rows:
            self.tree_id+=1
            print(self.tree_id," out of {} maps".format(len(rows)))
            self.drawOneDecisionTree(row['m_map'])
    # 특정 map 형태
    # 모든 distinct 한 map들에 대해 tree를 그린다. distinct map개수가 곧 tree의 개수

    def insertDecesionTree(self,idNum,sit_turn,sit_map,decisionTree,num_next_map):
        insert_tree_sql = """REPLACE INTO sampleomok.decision_trees(idNum,sit_turn,sit_map,num_next_map,decision_tree) VALUES({},{},'{}',{},'{}') """
        self.cur_raw.execute(insert_tree_sql.format(idNum,sit_turn,sit_map,num_next_map,decisionTree))
        self.cnx_data.commit()

    def insertLabeledMap(self,idNum,label,map):
        insert_map_sql =""" REPLACE INTO sampleomok.map_label(idNum,label,next_map) VALUES({},{},'{}') """
        self.cur_raw.execute(insert_map_sql.format(idNum,label,map))
        self.cnx_data.commit()

    def drawOneDecisionTree(self,sit_map):
        counter = 0
        int_sit_map = []

        for row in sit_map.split('], ['):
            if row[:2] == "[[":
                row = row[2:]
            int_sit_map.append(np.fromstring(row, dtype=int, sep=', '))

        for row in int_sit_map:
            for cell in row:
                counter+=1 if cell != 0 else 0
        target_turn = counter
        print("this is ",counter,"th turn situation ")
        # print(int_sit_map)
        # print(sit_map)

        # sit_map 과 똑같이 둔 적이 있는 idGame 모두 찾아서 gameList에 저장.
        specific_map_sql = """
        SELECT idGame,idTurn,m_map FROM sampleomok.sit_rep_turn as t WHERE m_map = '{0}' 
        """
        self.cur_raw.execute(specific_map_sql.format(sit_map))
        rows = self.cur_raw.fetchall()
        gameList = []

        for row in rows:
            gameList.append(row['idGame'])
            # target_turn = row['idTurn']
        # print('list of games with same map: ', gameList)

        # 위에서 추린 idgame 들 대상으로 target_turn+1턴의 map상태들을 feature로 해서 decisiontree그리기

        # to give list to mySql
        if len(gameList) <= 1:
            sql_gameList = str(gameList[0])
        else:
            sql_gameList = ','.join(map(str, gameList))

        tree_sql = '''
        SELECT t.idGame,t.idTurn,t.m_map,g.gameResult FROM sampleomok.sit_rep_turn as t JOIN sampleomok.sit_rep_game as g ON t.idGame=g.idGame WHERE t.idGame in ({0}) AND t.idTurn = {1} '''
        # n+1 턴의 맵들을 mapList에 저장
        mapList = []
        self.cur_raw.execute(tree_sql.format(sql_gameList, target_turn + 1))
        rows = self.cur_raw.fetchall()
        # if sit_map is last turn, there is no next turn
        if len(rows) == 0:
            print('this was the last turn')
            return False
        for row in rows:
            mapList.append(str(row['m_map']))
        count_nextmap_sql='''
        SELECT COUNT(DISTINCT t.m_map) as num_next_map FROM sampleomok.sit_rep_turn as t JOIN sampleomok.sit_rep_game as g ON t.idGame=g.idGame WHERE t.idGame in ({0}) AND t.idTurn = {1} '''
        self.cur_raw.execute(count_nextmap_sql.format(sql_gameList, target_turn + 1))
        next_map_count = self.cur_raw.fetchone()['num_next_map']

        # mapList들은 str이라 categorical data이기 때문에 LabelEncoder 이용해서 숫자로 바꾸는 과정.
        data = pd.read_sql(tree_sql.format(sql_gameList, target_turn + 1), self.cnx_data)
        df = pd.DataFrame(data)
        feature_df = df.drop(columns=['idGame', 'idTurn', 'gameResult']) # only m_map left

        feature_df_list = feature_df['m_map'].tolist()
        # print(len(feature_df_list))
        le= preprocessing.LabelEncoder()
        le.fit(feature_df_list)

        labeled_feature = le.transform(feature_df_list)
        labeled_feature = labeled_feature.reshape(-1, 1)
        label_list=[]
        for num in labeled_feature:
            if num[0] not in label_list:
                label_list.append(num[0])
                # print(self.tree_id, num[0]," , ", le.inverse_transform([num[0]])[0])
                self.insertLabeledMap(self.tree_id,num[0],le.inverse_transform([num[0]])[0])


        target_df = df['gameResult']
        split_train = False
        classifier = tree.DecisionTreeClassifier(criterion='entropy')
        script =''
        if split_train:
            from sklearn.model_selection import train_test_split

            feature_train, feature_test, target_train, target_test = train_test_split(labeled_feature, target_df, test_size=0.2)

            classifier.fit(feature_train, target_train)

            print("score", classifier.score(feature_train, target_train))
            print(classifier.score(feature_test, target_test))
        else:
            classifier.fit(labeled_feature,target_df)

            print("score",classifier.score(labeled_feature,target_df))

            tp = TreeParser.TreeParser()
            # print(target_df)
            script = tp.tree_to_code(classifier,['m_map'],target_df)
            # print(script)

    # -----------------------------------------------------------------

        import graphviz
        from IPython.display import Image, display

        file_output =False
        if file_output:
            dot_data = tree.export_graphviz(classifier, feature_names=list(feature_df.columns.values), out_file="tree.dot",
                                        filled=True, rounded=True, impurity=False)
            graph = graphviz.Source(dot_data)

            with open("tree.dot", encoding='UTF-8') as f:
                dot_graph = f.read()
            display(graphviz.Source(dot_graph))
            dot = graphviz.Source(dot_graph)
            dot.format = 'png'
            dot.render(filename='tree.png')
        else:
            dot_data = tree.export_graphviz(classifier, feature_names=list(feature_df.columns.values), out_file=None,
                                        impurity=False)
            # print(dot_data)
            self.insertDecesionTree(self.tree_id,target_turn,sit_map,script,next_map_count)


    def main(self):
        self.iterMaps()

if __name__ == '__main__':
    print("this is demo mode")
    drawtree = DrawTree()
    drawtree.main()