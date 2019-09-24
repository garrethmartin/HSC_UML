using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace GNGConsoleApp
{
    public class Utils
    {
        public static bool CompareData(List<float[]> samples, List<float[]> samples2)
        {
            //bool same = false;
            if (samples.Count != samples2.Count)
            {
                Console.WriteLine("counts are different");
                return false;
            }
            if (samples[0].Length != samples2[0].Length)
            {
                Console.WriteLine("counts are different");
                return false;
            }

            int numDims = samples[0].Length;

            for (int i = 0; i < samples.Count; i++)
            {
                for (int j = 0; j < numDims; j++)
                {
                    float a = samples[i][j];
                    float b = samples2[i][j];
                    if (a < 100 && Math.Abs(a - b) > 0.0001)
                        Console.WriteLine("different");
                    else
                    {
                        if (a > 100 && Math.Abs(a - b) > 0.2)
                            Console.WriteLine("different");
                    }
                }
            }

            return true;
        }
    }
}
