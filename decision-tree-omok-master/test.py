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

exec(decision_tree_str)
print(tree(1))
