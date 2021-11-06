import os
from sklearn.tree import _tree
file = open("tree.dot", "r", encoding='UTF-8')
startLine=3
# for line in file.read()[startLine:]:

class TreeParser:


    def __init__(self):
        self.script = ''


    def tree_to_code(self,tree, feature_names,target_df):

        # Outputs a decision tree model as a Python function
        #
        # Parameters:
        # -----------
        # tree: decision tree model
        #     The decision tree to represent as a function
        # feature_names: list
        #     The feature names of the dataset used for building the decision tree
        script = ""

        tree_ = tree.tree_
        for i in tree_.feature:
            # print(feature_names[i])
            feature_name = [
                feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
                for i in tree_.feature
            ]

        # print("def tree({}):".format(", ".join(feature_names)))
        self.script+=("def tree({}):\n".format(", ".join(feature_names)))

        def recurse(node, depth):
            indent = "  " * depth
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                # print ("{}if {} <= {}:".format(indent, name, threshold))
                self.script += "{}if {} <= {}:\n".format(indent, name, threshold)
                recurse(tree_.children_left[node], depth + 1)
                # print ("{}else:  # if {} > {}".format(indent, name, threshold))
                self.script += "{}else:  # if {} > {}\n".format(indent, name, threshold)
                recurse(tree_.children_right[node], depth + 1)
            else:
                # print ("{}return {}".format(indent, tree_.value[node]))

                if len(tree_.value[node][0]) <= 1:
                    if len(target_df.unique()) <= 1: # two if means same. use for sure
                        if target_df[0] == 'lose':
                            self.script += "{}return {}\n".format(indent, [tree_.value[node][0][0],0])
                        else:
                            self.script += "{}return {}\n".format(indent, [0,tree_.value[node][0][0]])
                    else:
                        print("WHAAATTT??")


                elif len(tree_.value[node][0]) == 2:
                    self.script += "{}return {}\n".format(indent, [tree_.value[node][0][0], tree_.value[node][0][1]])
                else:
                    print("longer than 2? something weird")

        recurse(0, 1)
        # print("this is lose count", target_df.value_counts()['lose'])
        return self.script

    def export_to_file(script,tree_name):
        f =open(tree_name,"x")
        f.write(script)
        f.close()


# print("dt type",type(dt.classifier))
# print("feature names type",type(list(dt.feature_train)))
# print(list(dt.feature_train))

