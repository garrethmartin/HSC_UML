mkdir ConnComponents
cd ConnComponents

dotnet new sln
dotnet new classlib -o Config -f netcoreapp2.0
dotnet new classlib -o CSVParser -f netcoreapp2.0
dotnet new console -o ConnectedComponents -f netcoreapp2.0

dotnet new classlib -o NearestNeighbourLib -f netcoreapp2.0
dotnet new classlib -o SampleHandlerLib -f netcoreapp2.0

dotnet sln ConnComponents.sln add Config/Config.csproj
dotnet sln ConnComponents.sln add CSVParser/CSVParser.csproj
dotnet sln ConnComponents.sln add NearestNeighbourLib/NearestNeighbourLib.csproj
dotnet sln ConnComponents.sln add SampleHandlerLib/SampleHandlerLib.csproj
dotnet sln ConnComponents.sln add ConnectedComponents/ConnectedComponents.csproj

dotnet add ConnectedComponents/ConnectedComponents.csproj reference Config/Config.csproj
dotnet add ConnectedComponents/ConnectedComponents.csproj reference CSVParser/CSVParser.csproj
dotnet add ConnectedComponents/ConnectedComponents.csproj reference NearestNeighbourLib/NearestNeighbourLib.csproj
dotnet add ConnectedComponents/ConnectedComponents.csproj reference SampleHandlerLib/SampleHandlerLib.csproj

dotnet add package System.Drawing.Common --version 4.5.0-preview1-26216-02 
rem https://www.nuget.org/packages/System.Drawing.Common/