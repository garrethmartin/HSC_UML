#!/bin/bash

set -e

cd graph_clustering/code/dotnetcore/GNG
dotnet build --configuration Release

cd ../ConnComponents
dotnet build --configuration Release

cd ../AgglomerativeClustering
dotnet build --configuration Release

cd ../dotnetcore/GNG
dotnet build --configuration Release

cd ../ConnComponents
dotnet build --configuration Release

cd ../AgglomerativeClustering
dotnet build --configuration Release

cd ../../../..
