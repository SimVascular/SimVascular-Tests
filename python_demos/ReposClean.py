from sv import Repository
objs = Repository.List()
for name in objs:
    Repository.Delete(name)
    
