class Group:
  def __init__(self, l, r):
    self.prev = None
    self.next = None
    self.l = l
    self.r = r
    self.ls = None

  def removeRecord(self):
    size = self.size()
    if self.ls.sizes[size] == 1:
      del self.ls.sizes[size]
    else:
      self.ls.sizes[size] -= 1
    self.ls.index[self.l] = None
    self.ls.index[self.r] = None

  def addRecord(self):
    self.ls.sizes[self.size()] += 1
    self.ls.index[self.l] = self
    self.ls.index[self.r] = self
  
  def size(self):
    return self.r - self.l + 1 if self.l <= self.r else self.ls.n - self.l + self.r + 1

  def __str__(self):
    return str((self.l, self.r))

class GroupsList:
  def __init__(self, n):
    self.n = n
    self.clear()

  def insert(self, node, prev):
    node.prev = prev
    node.next = prev.next
    prev.next = node
    if node.next:
      node.next.prev = node
    if self.tail == prev:
      self.tail = node
    self.size += 1
    node.ls = self
    node.addRecord()
    return self

  def append(self, node):
    node.next = None
    if self.tail:
      self.tail.next = node
      node.prev = self.tail
      self.tail = node
    else:
      self.head = node
      self.tail = node
    self.size += 1
    node.ls = self
    node.addRecord()
    return self
  
  def pop(self, node):
    if node.prev:
      node.prev.next = node.next
    if node.next:
      node.next.prev = node.prev
    if self.head == node:
      self.head = node.next
    if self.tail == node:
      self.tail = node.prev
    node.next = None
    node.prev = None
    self.size -= 1
    node.removeRecord()
    return self
  
  def clear(self):
    self.head = None
    self.tail = None
    self.sizes = defaultdict(int)
    self.index = [None] * self.n
    self.size = 0
    return self
  
  def __str__(self):
    ls = []
    node = self.head
    while node:
      ls.append(str(node))
      node = node.next
    return '[' + ', '.join(ls) + f'] {self.head} -> {self.tail}'

  def __len__(self):
    return self.size

class Solution:
  def sizeCheck(self, size):
    ans = 0
    if len(self.groups): # index check
      for group_size, groups_count in self.groups.sizes.items():
        if group_size >= size:
          ans += (group_size - size + 1) * groups_count
    elif size <= self.n: # ouroboros
      ans = self.n
    return ans
  
  # operation types (changing index 2)
  # [10][0][01] -> [10101]         single merge
  # [10101] -> [10][0][01]         single split
  # .010][0][01. -> .010101. -> .. single ouroboros merge
  # .. -> .010101. -> .010][0][01. single ouroboros split
  # [101][101] -> [10][0101]       shift right
  # [10][0101] -> [101][101]       shift left
  def colorChange(self, index, color):
    if self.colors[index] == color or index < 0 or index >= self.n:
      return
    self.colors[index] = color
    if len(self.groups):
      if self.groups.index[index]: # direct record match
        if self.groups.index[index].l == self.groups.index[index].r:
          self.singleMerge(self.groups.index[index])
        elif self.groups.index[index].l == index:
          self.shiftLeft(self.groups.index[index])
        elif self.groups.index[index].r == index:
          self.shiftRight(self.groups.index[index])
      else: # inside record search
        pointer = index
        while not self.groups.index[pointer]:
          if not pointer:
            pointer = self.n
          pointer -= 1
        self.singleSplit(self.groups.index[pointer], index)
    else:
      self.singleOuroborosSplit(index)
  
  def singleMerge(self, group):
    prev_group = group.prev if group.prev else self.groups.tail
    next_group = group.next if group.next else self.groups.head
    if prev_group == next_group: # single ouroboros merge
      self.groups.clear()
    else: # single merge
      (self.groups
        .pop(next_group)
        .pop(prev_group))
      group.removeRecord()
      group.l = prev_group.l
      group.r = next_group.r
      group.addRecord()

  def singleOuroborosSplit(self, index):
    (self.groups
      .append(Group(self.inc(index), self.dec(index)))
      .append(Group(index, index)))

  def singleSplit(self, group, index):
    group.removeRecord()
    center_group = Group(index, index)
    next_group = Group(self.inc(index), group.r)
    (self.groups
      .insert(center_group, group)
      .insert(next_group, center_group))
    group.r = self.dec(index)
    group.addRecord()

  def shiftLeft(self, group):
    prev_group = group.prev if group.prev else self.groups.tail
    group.removeRecord()
    if group == prev_group:
      group.r = group.l
    else:
      prev_group.removeRecord()
      prev_group.r = group.l
      prev_group.addRecord()
    group.l = self.inc(group.l)
    group.addRecord()

  def shiftRight(self, group):
    next_group = group.next if group.next else self.groups.head
    group.removeRecord()
    if group == next_group:
      group.l = group.r
    else:
      next_group.removeRecord()
      next_group.l = group.r
      next_group.addRecord()
    group.r = self.dec(group.r)
    group.addRecord()

  def dec(self, index):
    return index - 1 if index else self.n - 1

  def inc(self, index):
    return (index + 1) % self.n

  def numberOfAlternatingGroups(self, colors: List[int], queries: List[List[int]]) -> List[int]:
    self.colors = colors
    self.n = len(colors)
    self.groups = GroupsList(self.n)
    
    # fill groups list
    f = 0 if colors[0] == colors[-1] else None
    l = f
    for r in range(1, self.n):
      if colors[r] == colors[r - 1]:
        if f == None:
          f = r
        else:
          self.groups.append(Group(l, r - 1))
        l = r
    if f != None:
      self.groups.append(Group(l, self.dec(f)))
      
    # process queries
    ans = []
    for query in queries:
      if query[0] == 2:
        self.colorChange(query[1], query[2])
      else:
        ans.append(self.sizeCheck(query[1]))

    return ans
