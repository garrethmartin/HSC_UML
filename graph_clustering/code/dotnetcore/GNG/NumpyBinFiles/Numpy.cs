using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.IO;
using System.Text.RegularExpressions;

namespace NumpyBinFiles
{
    /// <summary>
    /// https://docs.scipy.org/doc/numpy/neps/npy-format.html
    /// </summary>
    public class Numpy
    {
        public static List<float[]> ReadFile(String filePath)
        {
            List<float[]> data = new List<float[]>();

            long fileSize = new FileInfo(filePath).Length;
            long rowCount = 0L;
            long position = 0L;
            while (position < fileSize)
            {
                Header header = Header.ParseHeader(filePath, position);
                rowCount += header.NumRows;
                Console.WriteLine("Read header: " + header);
                position = ReadFilePart(header, data, filePath);
            }
            Console.WriteLine("Rows output: {0}", data.Count);
            if (rowCount != data.Count)
                Console.WriteLine("Error: row count mismatch");
            return data;
        }

        private static long ReadFilePart(Header header, List<float[]> data, String filePath)
        {
            long finalPosition = 0L;

            using (FileStream fs = File.OpenRead(filePath))
            {
                // move to the start of the data position
                long res = fs.Seek(header.DataStartPos, SeekOrigin.Begin);

                BinaryReader br = new BinaryReader(fs);
                for (int row = 0; row < header.NumRows; row++)
                {
                    float[] dataRow = new float[header.NumCols];
                    for (int col = 0; col < header.NumCols; col++)
                    {
                        dataRow[col] = br.ReadSingle();
                    }
                    data.Add(dataRow);
                    if (row % 1000000 == 0)
                        Console.WriteLine(row);
                }
                finalPosition = fs.Position;
            }

            return finalPosition;
        }

        public List<float[]> ReadBinFile(String filePath)
        {
            List<float[]> data = new List<float[]>();

            int headerLen = 80;
            long numRows = -1;
            long numCols = -1;

            // read header
            using (FileStream fs = File.OpenRead(filePath))
            {
                long length = fs.Length;
                byte[] headerBytes = new byte[headerLen];
                int res = fs.Read(headerBytes, 0, headerBytes.Length);
                String header = System.Text.Encoding.ASCII.GetString(headerBytes).Trim();

                // parse header
                //header = 'rows={0},cols={1}'.format(dat_file.shape[0], dat_file.shape[1])
                String pattern = @"rows=([0-9]+),cols=([0-9]+)";
                Regex rgx = new Regex(pattern);
                Match m = rgx.Match(header);
                if (m.Success)
                {
                    numRows = UInt32.Parse(m.Groups[1].Value);
                    numCols = UInt32.Parse(m.Groups[2].Value);
                }

                BinaryReader br = new BinaryReader(fs);
                for (int row = 0; row < numRows; row++)
                {
                    float[] dataRow = new float[numCols];
                    for (int col = 0; col < numCols; col++)
                    {
                        dataRow[col] = br.ReadSingle();
                    }
                    data.Add(dataRow);
                    if (row % 100000 == 0)
                        Console.WriteLine(row);
                }

            }

            return data;
        }
    }
}

