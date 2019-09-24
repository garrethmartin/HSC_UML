using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.IO;

namespace GNGConsoleApp
{
    public class DataReader
    {

        public void test()
        {
            using (FileStream fr = File.Open(@"n:\atlas\bovw\dat.bin", FileMode.Open))
            {
                // http://stackoverflow.com/questions/265639/net-c-sharp-random-access-in-text-files-no-easy-way
                BinaryReader br = new BinaryReader(fr);
                for (int i = 0; i < 10; i++)
                {
                    byte[] num = br.ReadBytes(4);

                    float myFloat = System.BitConverter.ToSingle(num, 0);
                    Console.WriteLine(myFloat);
                }

            }
        }
    }
}
