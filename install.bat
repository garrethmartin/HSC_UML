@echo off


cd graph_clustering\code\dotnetcore\GNG
dotnet build --configuration Release || goto :error

cd ..\ConnComponents
dotnet build --configuration Release || goto :error

cd ..\AgglomerativeClustering
dotnet build --configuration Release || goto :error

cd ..\dotnetcore\GNG
dotnet build --configuration Release || goto :error

cd ..\ConnComponents
dotnet build --configuration Release || goto :error

cd ..\AgglomerativeClustering
dotnet build --configuration Release || goto :error

cd ..\..\..\..

goto :EOF


:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%