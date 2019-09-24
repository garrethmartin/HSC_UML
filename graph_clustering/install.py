import os
current_dir = os.getcwd()

print('Installing GNG')

os.chdir(current_dir+'/code/dotnetcore/GNG')
os.system('dotnet build --configuration Release')
os.chdir(current_dir)

print ('Installing ConnectedComponents')

os.chdir(current_dir+'/code/dotnetcore/ConnComponents')
os.system('dotnet build --configuration Release')
os.chdir(current_dir)

print ('Installing Clustering')

os.chdir(current_dir+'/code/dotnetcore/AgglomerativeClustering/')
os.system('dotnet build --configuration Release')
os.chdir(current_dir)