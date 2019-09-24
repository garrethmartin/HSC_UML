mkdir AgglomerativeClustering
cd AgglomerativeClustering

dotnet new sln
dotnet new classlib -o AgglomLib -f netcoreapp2.0
dotnet new console -o AgglomerativeClustering

dotnet new classlib -o Config -f netcoreapp2.0
dotnet new classlib -o CSVParser -f netcoreapp2.0
dotnet new classlib -o NearestNeighbourLib -f netcoreapp2.0

dotnet sln AgglomerativeClustering.sln add Config/Config.csproj
dotnet sln AgglomerativeClustering.sln add CSVParser/CSVParser.csproj
dotnet sln AgglomerativeClustering.sln add NearestNeighbourLib/NearestNeighbourLib.csproj
dotnet sln AgglomerativeClustering.sln add AgglomerativeClustering/AgglomerativeClustering.csproj
dotnet sln AgglomerativeClustering.sln add AgglomLib/AgglomLib.csproj

dotnet add AgglomerativeClustering/AgglomerativeClustering.csproj reference Config/Config.csproj
dotnet add AgglomerativeClustering/AgglomerativeClustering.csproj reference CSVParser/CSVParser.csproj
dotnet add AgglomerativeClustering/AgglomerativeClustering.csproj reference AgglomLib/AgglomLib.csproj
dotnet add AgglomerativeClustering/AgglomerativeClustering.csproj reference NearestNeighbourLib/NearestNeighbourLib.csproj


dotnet add AgglomLib/AgglomLib.csproj reference Config/Config.csproj
dotnet add AgglomLib/AgglomLib.csproj reference CSVParser/CSVParser.csproj

