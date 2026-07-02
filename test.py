from tools import web_search

result = web_search.invoke({"query": "Artificial Intelligence"})

print(type(result))
print(result)