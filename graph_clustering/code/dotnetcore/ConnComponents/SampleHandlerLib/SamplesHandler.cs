using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace SampleHandlerLib
{
    
    public class SamplesHandler
    {
        public void SaveNorm(String filePath, ZScore z)
        {
            using (StreamWriter sw = new StreamWriter(filePath + "/mean.txt"))
            {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < z.Mu.Length; i++)
                {
                    sb.Append(z.Mu[i]);
                    if (i < z.Mu.Length - 1)
                        sb.Append(", ");
                }
                sw.WriteLine(sb);
            }
            using (StreamWriter sw = new StreamWriter(filePath + "/std.txt"))
            {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < z.Std.Length; i++)
                {
                    sb.Append(z.Std[i]);
                    if (i < z.Std.Length - 1)
                        sb.Append(", ");
                }
                sw.WriteLine(sb);
            }
        }
    }
}
