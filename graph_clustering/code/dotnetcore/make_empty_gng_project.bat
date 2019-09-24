mkdir GNG
cd GNG
dotnet new sln

dotnet new classlib -o Config -f netcoreapp2.0
dotnet new classlib -o CsvParser -f netcoreapp2.0
dotnet new classlib -o GrowingNeuralGas -f netcoreapp2.0
dotnet new console -o GNGConsoleApp -f netcoreapp2.0

dotnet new classlib -o NumpyBinFiles -f netcoreapp2.0
dotnet new console -o NumpyTest -f netcoreapp2.0

dotnet sln GNG.sln add Config/Config.csproj
dotnet sln GNG.sln add CsvParser/CsvParser.csproj
dotnet sln GNG.sln add GrowingNeuralGas/GrowingNeuralGas.csproj
dotnet sln GNG.sln add GNGConsoleApp/GNGConsoleApp.csproj

dotnet sln GNG.sln add NumpyBinFiles/NumpyBinFiles.csproj
dotnet sln GNG.sln add NumpyTest/NumpyTest.csproj

dotnet add GNGConsoleApp/GNGConsoleApp.csproj reference Config/Config.csproj
dotnet add GNGConsoleApp/GNGConsoleApp.csproj reference CsvParser/CsvParser.csproj
dotnet add GNGConsoleApp/GNGConsoleApp.csproj reference GrowingNeuralGas/GrowingNeuralGas.csproj 
dotnet add GNGConsoleApp/GNGConsoleApp.csproj reference NumpyBinFiles/NumpyBinFiles.csproj
dotnet add GrowingNeuralGas/GrowingNeuralGas.csproj reference CsvParser/CsvParser.csproj
