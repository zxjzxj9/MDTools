// This program intend to calculate RDF of the triclinic crystal
// Aimed at shared library called by C
// By zxj, 2016/4/7
// g_ab = \frac{n_ab(r)}{4*\pi*r^2dr\rho_a}
// Where \rho_a = V/(N*c_a)

// na: number of atom a 
// aser: atom serial number of a
// nb: number of atom b
// bser: atom serial number of b
// ntot: total number of atoms
// coord: coordinate of atoms
// latt: 3x3 lattice
// nbins: number of bins
// binsize: the size of each bins
// RDF: final output radial distribution function
// lattice
//   vecA     vecB     vecC
// | latt[0]  latt[1]  latt[2] |
// | latt[3]  latt[4]  latt[5] |
// | latt[6]  latt[7]  latt[8] |

#include <math.h>
#include <string.h>
#define sqdist(vec) (vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2])
#define sq(num) (num*num)
#define MX 1
#define MY 1
#define MZ 1
#define MGRID MX*MY*MZ
#define PI 3.1415926

void basicRDF(int na, int* aser, int nb, int* bser, int ntot, double* coord, double* latt, int nbins, double binsize, double *RDF)
{
    int i,j;
    int nx,ny,nz; // maybe slower
    double vol = latt[0] * latt[4] * latt[8];
    double tmpVec1[3], tmpVec2[3];
    double d1;
    double dens = vol/na;

    memset((void*) RDF, 0, nbins*sizeof(double)); // clear the RDF data

    for(i = 0; i < na; i++)
    {
        for(j = 0; j < nb; j++)
        {
            tmpVec1[0] = coord[3*aser[i]  ] - coord[3*bser[j]  ];         
            tmpVec1[1] = coord[3*aser[i]+1] - coord[3*bser[j]+1];         
            tmpVec1[2] = coord[3*aser[i]+2] - coord[3*bser[j]+2];         
            
            for(nx = -MX; nx < MX+1; nx++)
            {
                for(ny = -MY; ny < MY+1; ny++)
                {
                    for(nz = -MZ; nz < MZ+1; nz++)
                    {
                        tmpVec2[0] = tmpVec1[0] + nx*latt[0] + ny*latt[1] + nz*latt[2];  
                        tmpVec2[1] = tmpVec1[1] + nx*latt[3] + ny*latt[4] + nz*latt[5];
                        tmpVec2[2] = tmpVec1[2] + nx*latt[6] + ny*latt[7] + nz*latt[8];
                        d1 = sqrt(sqdist(tmpVec2));
                        if(d1 < nbins*binsize)
                        {
                           RDF[(int) floor(d1/binsize)] += 1.00/(4*PI*sq(d1)*binsize*dens);
                        }
                    }
                }
            } 
        }
    } 

    return;
}
