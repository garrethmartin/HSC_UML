using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;

namespace ConnectedComponents
{
    public class ObjectCentre
    {
        public int X;
        public int Y;
        public int Strength;
        public List<ObjectCentre> BlobCentres;
        public int HACClusterId;
        public bool IsMaster;
        public Rectangle Rect;
        public ObjectCentre()
        {

        }

        public ObjectCentre(int x, int y, int strength, bool isMaster = false)
        {
            this.X = x;
            this.Y = y;
            this.Strength = strength;
            this.IsMaster = isMaster;
            this.BlobCentres = new List<ObjectCentre>();
        }

        public ObjectCentre(int x, int y, Rectangle rect, int strength, int clusterId, bool isMaster=false)
        {
            this.X = x;
            this.Y = y;
            this.Strength = strength;
            this.BlobCentres = new List<ObjectCentre>();
            this.HACClusterId = clusterId;
            this.IsMaster = isMaster;
            this.Rect = rect;
        }

        public int Distance(ObjectCentre oc)
        {
            int diffX = (oc.X - this.X);
            int diffY = (oc.Y - this.Y);
            int dist = (int)Math.Sqrt(Math.Pow(diffX, 2) + Math.Pow(diffY, 2));
            return dist;
        }

    }
}
