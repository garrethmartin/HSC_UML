using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AgglomerativeClustering
{
    public interface Similarity
    {
        double GetDistance(BiCluster one, BiCluster two);
    }

}
