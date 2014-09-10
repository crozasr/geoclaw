r"""
fgmax_tools module: $CLAW/geoclaw/src/python/geoclaw/fgmax_tools.py

Tools to specify an fgmax grid for keeping track of maximum flow depth, etc.
and to read in the fgmax output after doing a GeoClaw run.

"""

from clawpack.geoclaw import kmltools
import os
from numpy import sqrt, ma
import numpy


class FGmaxGrid(object):

    """
    New class introduced in 5.2.1 to keep store information both about the
    fgmax input data and the output generated by a GeoClaw run.
    """

    def __init__(self):
        self.point_style = None
        self.npts = None
        self.nx = None
        self.ny = None
        self.n12 = None
        self.n23 = None
        self.tstart_max =  0.
        self.tend_max = 1.e10   # when to stop monitoring max values
        self.dt_check = 10.     # target time (sec) increment between updating 
                                # max values
        self.min_level_check = None    # which levels to monitor max on
        self.arrival_tol = 1.e-2       # tolerance for flagging arrival
        self.input_file_name = 'fgmax.txt'  # file for GeoClaw input data
        self.fgno = 1  # FG number

        self.outdir = '_output'    # where to find GeoClaw output fort.FG*
        self.level = None
        self.x = None
        self.y = None
        self.dx = None
        self.dy = None
        self.B = None
        self.h = None
        self.h_time = None
        self.s = None
        self.s_time = None
        self.hs = None
        self.hs_time = None
        self.hss = None
        self.hss_time = None
        self.hmin = None
        self.hmin_time = None
        self.arrival_time = None

    def read_input_data(self, input_file_name=None):
        r"""
        Read input data from a file like *fgmax.txt* that
        might have been created by *write_input_data*.
        """

        if input_file_name is not None:
            self.input_file_name = input_file_name
        fgmax_input = open(self.input_file_name).readlines()

        self.tstart_max = float(fgmax_input[0].split()[0])
        self.tend_max = float(fgmax_input[1].split()[0])
        self.dt_check = float(fgmax_input[2].split()[0])
        self.min_level_check = int(fgmax_input[3].split()[0])
        self.arrival_tol = float(fgmax_input[4].split()[0])
        self.point_style = point_style = int(fgmax_input[5].split()[0])
        if point_style in [0,1]:
            self.npts = npts = int(fgmax_input[6].split()[0])
        elif point_style == 2:
            self.nx = nx = int(fgmax_input[6].split()[0])
            self.ny = ny = int(fgmax_input[6].split()[1])
        elif point_style == 3:
            self.n12 = n12 = int(fgmax_input[6].split()[0])
            self.n23 = n23 = int(fgmax_input[6].split()[1])
        if point_style == 1:
            self.x, self.y = numpy.loadtxt(fgmax_input, skiprows=7, unpack=True)


    def write_input_data(self, input_file_name=None):
        r"""
        Write input data from a file like *fgmax.txt* that
        will be read in by GeoClaw as input data.
        """

        if input_file_name is not None:
            self.input_file_name = input_file_name

        print "---------------------------------------------- "
        x1,x2 = self.x1, self.x2
        y1,y2 = self.y1, self.y2
        point_style = self.point_style
        if point_style not in [1,2,3]:
            raise NotImplementedError("make_fgmax not implemented for point_style %i" \
                % point_style)

        if point_style == 2:
            # 2d grid of points
            if self.nx is None:
                dx = self.dx
                nx = int(round((x2-x1)/dx)) + 1  
                if abs((nx-1)*dx + x1 - x2) > 1e-6:
                    print "Warning: abs((nx-1)*dx + x1 - x2) = ", \
                          abs((nx-1)*dx + x1 - x2)
                    print "         old x2: %22.16e" % x2
                    x2 = x1 + dx*(nx-1)
                    print "         resetting x2 to %22.16e" % x2
            else:
                nx = self.nx
                dx = (x2-x1)/(nx+1.)
                if self.dx is not None:
                    print "*** Warning: dx specified over-ridden by: ",dx
        
            if self.ny is None:
                dy = self.dy
                if dy is None:
                    dy = dx
                ny = int(round((y2-y1)/dy)) + 1  
                if abs((ny-1)*dy + y1 - y2) > 1e-6:
                    print "Warning: abs((ny-1)*dy + y1 - y2) = ", \
                          abs((ny-1)*dy + y1 - y2)
                    print "         old y2: %22.16e" % y2
                    y2 = y1 + dy*(ny-1)
                    print "         resetting y2 to %22.16e" % y2
            else:
                ny = self.ny
                dy = (y2-y1)/(ny+1.)
                if self.dy is not None:
                    print "*** Warning: dy specified over-ridden by: ",dy
        
        
            npts = nx*ny
        
            fid = open(self.input_file_name,'w')
            fid.write("%16.10e            # tstart_max\n"  % self.tstart_max)
            fid.write("%16.10e            # tend_max\n"  % self.tend_max)
            fid.write("%16.10e            # dt_check\n" % self.dt_check)
            fid.write("%i %s              # min_level_check\n" \
                                % (self.min_level_check,16*" "))

            fid.write("%16.10e            # arrival_tol\n" % self.arrival_tol)
            fid.write("%i %s              # point_style\n" \
                                % (self.point_style,16*" "))
        
            fid.write("%i  %i %s          # nx,ny\n" \
                                % (nx,ny,10*" "))
            fid.write("%16.10e   %20.10e            # x1, y1\n" % (x1,y1))
            fid.write("%16.10e   %20.10e            # x2, y2\n" % (x2,y2))
            fid.close()
            
        
            print "Created file ", self.input_file_name
            print "   specifying fixed grid with shape %i by %i, with  %i points" \
                    % (nx,ny,npts)
            print "   lower left  = (%15.10f,%15.10f)" % (x1,y1)
            print "   upper right = (%15.10f,%15.10f)" % (x2,y2)
            print "   dx = %15.10e,  dy = %15.10e" % (dx,dy)
        
            xy = [x1,x2,y1,y2]
            fname_root = os.path.splitext(self.input_file_name)[0]
            kml_file = fname_root + '.kml'
            kmltools.box2kml(xy, kml_file, fname_root, color='8888FF')

        elif point_style==1:
            # 1d transect of points
            if self.npts is None:
                dx = self.dx
                npts = int(round(sqrt((x2-x1)**2 + (y2-y1)**2)/dx)) + 1
                if abs((npts-1)*dx + x1 - x2) > 1e-6:
                    print "Warning: abs((npts-1)*dx + x1 - x2) = ", \
                          abs((npts-1)*dx + x1 - x2)
                    x2 = x1 + dx*(npts-1)
                    y2 = y1 + dx*(npts-1)
                    print "         resetting x2 to %g" % x2
                    print "         resetting y2 to %g" % y2
            else:
                npts = self.npts
                dx = sqrt((x2-x1)**2 + (y2-y1)**2)/(npts+1.)
                if self.dx is not None:
                    print "*** Warning: dx specified over-ridden by: ",dx
        
        
            print "Creating 1d fixed grid with %s points" % npts
            print "   dx = %g" % dx
        
            fid = open(self.fname,'w')
            fid.write("%g                 # tstart_max\n"  % self.tstart_max)
            fid.write("%g                 # tend_max\n"  % self.tend_max)
            fid.write("%g                 # dt_check\n" % self.dt_check)
            fid.write("%i                 # min_level_check\n" % self.min_level_check)
            fid.write("%g                 # arrival_tol\n" % self.arrival_tol)
            fid.write("%g                 # point_style\n" % self.point_style)
        
            fid.write("%i                 # npts\n" % (npts))
            fid.write("%g   %g            # x1, y1\n" % (x1,y1))
            fid.write("%g   %g            # x2, y2\n" % (x2,y2))
            fid.close()
            
        
            print "Created file ", self.fname
            print "   specifying fixed grid with %i points equally spaced from " \
                    % npts
            print "   (%g,%g)  to  (%g,%g)" % (x1,y1,x2,y2)
            
            # not yet implemented:
            #fname_root = os.path.splitext(self.fname)[0]
            #kml_file = fname_root + '.kml'
            #kmltools.line2kml(xy, kml_file, fname_root, color='8888FF')

        elif point_style==3:
            # arbitrary quadrilateral
            x3,x4 = self.x3, self.x4
            y3,y4 = self.y3, self.y4
            if self.n12 is None:
                raise NotImplementedError("Need to set n12 and n23")
            else:
                npts = self.n12 * self.n23
        
        
            fid = open(self.fname,'w')
            fid.write("%g                 # tstart_max\n"  % self.tstart_max)
            fid.write("%g                 # tend_max\n"  % self.tend_max)
            fid.write("%g                 # dt_check\n" % self.dt_check)
            fid.write("%i                 # min_level_check\n" % self.min_level_check)
            fid.write("%g                 # arrival_tol\n" % self.arrival_tol)
            fid.write("%g                 # point_style\n" % self.point_style)
        
            fid.write("%i  %i %s          # self.n12,self.n23\n" \
                                % (self.n12,self.n23,10*" "))
            fid.write("%16.10e   %20.10e            # x1, y1\n" % (x1,y1))
            fid.write("%16.10e   %20.10e            # x2, y2\n" % (x2,y2))
            fid.write("%16.10e   %20.10e            # x3, y3\n" % (x3,y3))
            fid.write("%16.10e   %20.10e            # x4, y4\n" % (x4,y4))
            fid.close()
            
        
            print "Created file ", self.fname
            print "   specifying fixed grid as a quadrilateral"
            print "       %i by %i, with  %i points" \
                    % (self.n12,self.n23,npts)
            print "   corner 1 = (%15.10f,%15.10f)" % (x1,y1)
            print "   corner 2 = (%15.10f,%15.10f)" % (x2,y2)
            print "   corner 3 = (%15.10f,%15.10f)" % (x3,y3)
            print "   corner 4 = (%15.10f,%15.10f)" % (x4,y4)
            
            xy = [x1,y1,x2,y2,x3,y3,x4,y4]
            fname_root = os.path.splitext(self.fname)[0]
            kml_file = fname_root + '.kml'
            kmltools.quad2kml(xy, kml_file, fname_root, color='8888FF')

    def read_output(self, fgno=None, outdir=None):
        r"""
        Read the GeoClaw results on the fgmax grid numbered *fgno*.
        """
    
        if self.point_style is None:
            raise IOError("*** point_style is not set, need to read input?")
        point_style = self.point_style

        if fgno is not None:
            self.fgno = fgno
        if outdir is not None:
            self.outdir = outdir
    
        fname = self.outdir + '/fort.FG%s.valuemax' % self.fgno
        if not os.path.isfile(fname):
            raise IOError("File not found: %s" % fname)
        print "Reading %s ..." % fname
        d = numpy.loadtxt(fname)
    
        fname = os.path.join(self.outdir, '/fort.FG%s.aux1' % self.fgno)
        fname = self.outdir + '/fort.FG%s.aux1' % self.fgno
        if not os.path.isfile(fname):
            raise IOError("File not found: %s" % fname)
        print "Reading %s ..." % fname
        daux = numpy.loadtxt(fname)
    
        ncols = d.shape[1]  
        if ncols not in [6,8,14]:
            raise IOError("*** Unexpected number of columns %s in file %s" \
                    % (ncols, fname))
    
        ind_x = 0
        ind_y = 1
        ind_level = 2
        ind_h = 3
        if ncols == 6:
            ind_h_time = 4
            ind_arrival_time = 5
        elif ncols == 8:
            ind_s = 4
            ind_h_time = 5
            ind_s_time = 6
            ind_arrival_time = 7
        elif ncols == 14:
            ind_s = 4
            ind_hs = 5
            ind_hss = 6
            ind_hmin = 7
            ind_h_time = 8
            ind_s_time = 9
            ind_hs_time = 10
            ind_hss_time = 11
            ind_hmin_time = 12
            ind_arrival_time = 13
    
        if point_style in [0,1]:
            fg_shape = (self.npts,)
        elif point_style == 2:
            fg_shape = (self.nx,self.ny)
        elif point_style == 3:
            fg_shape = (self.n12,self.n23)
        else:
            raise NotImplemented("Not implemented for point_style %s" \
                % point_style)
    
        x = numpy.reshape(d[:,0],fg_shape,order='F')
        y = numpy.reshape(d[:,1],fg_shape,order='F')
        y0 = 0.5*(y.min() + y.max())   # mid-latitude for scaling plots
        h = numpy.reshape(d[:,ind_h],fg_shape,order='F')
    
        # AMR level used for each fgmax value:
        level = numpy.reshape(d[:,ind_level].astype('int'),fg_shape,order='F')
        
        topo = []
        nlevels = daux.shape[1]
        for i in range(2,nlevels):
            topoi = numpy.reshape(daux[:,i],fg_shape,order='F')
            topoi = ma.masked_where(topoi < -1e50, topoi)
            topo.append(topoi)
    
        B = ma.masked_where(level==0, topo[0])  # level==0 ==> never updated
        levelmax = level.max()
        for i in range(levelmax):
            B = numpy.where(level==i+1, topo[i], B)
    
        mask = (h < -1e50)  # points that were never set
        B = ma.masked_where(mask, B)
        h = ma.masked_where(mask, h)

        def set_q_time(ind_q, ind_q_time):  
            q = numpy.reshape(d[:,ind_q],fg_shape,order='F')
            q = ma.masked_where(mask,q) 
            q_time = numpy.reshape(d[:,ind_q_time],fg_shape,order='F')  
            q_time = ma.masked_where(mask, q_time)      
            return q, q_time
    
        self.h, self.h_time = set_q_time(ind_h, ind_h_time)
        if ncols > 6:
            self.s, self.s_time = set_q_time(ind_s, ind_s_time)
        if ncols > 8:
            self.hs, self.hs_time = set_q_time(ind_hs, ind_hs_time)
            self.hss, self.hss_time = set_q_time(ind_hss, ind_hss_time)
            self.hmin, self.hmin_time = set_q_time(ind_hmin, ind_hmin_time)
    
        # last column is arrival times:
        arrival_time = numpy.reshape(d[:,ind_arrival_time],fg_shape,order='F')
        arrival_time = ma.masked_where(arrival_time < -1e50, arrival_time)  
        arrival_time = ma.masked_where(mask, arrival_time)
        self.arrival_time = arrival_time
    
        self.level = level
        self.x = x
        self.y = y
        self.B = B
        self.h = h
    


## == Old versions now deprecated....

class fgmax_grid_parameters(object):

    """Deprecated -- use class fgmax """

    def __init__(self):
        self.point_style = 2      # expect 1 or 2
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.dx = None
        self.dy = None
        self.npts = None
        self.nx = None
        self.ny = None
        self.n12 = None
        self.n23 = None
        self.tstart_max =  0.
        self.tend_max = 1.e10     # when to stop monitoring max values
        self.dt_check = 10.       # target time (sec) increment between updating 
                                  # max values
        self.min_level_check = None    # which levels to monitor max on
        self.arrival_tol = 1.e-2    # tolerance for flagging arrival
        self.fname = 'fgmax_grid.txt'

def make_fgmax(FG):
    print "---------------------------------------------- "
    x1,x2 = FG.x1, FG.x2
    y1,y2 = FG.y1, FG.y2
    point_style = FG.point_style
    if point_style not in [1,2,3]:
        raise NotImplementedError("make_fgmax not implemented for point_style %i" \
            % point_style)

    if point_style == 2:
        # 2d grid of points
        if FG.nx is None:
            dx = FG.dx
            nx = int(round((x2-x1)/dx)) + 1  
            if abs((nx-1)*dx + x1 - x2) > 1e-6:
                print "Warning: abs((nx-1)*dx + x1 - x2) = ", \
                      abs((nx-1)*dx + x1 - x2)
                print "         old x2: %22.16e" % x2
                x2 = x1 + dx*(nx-1)
                print "         resetting x2 to %22.16e" % x2
        else:
            nx = FG.nx
            dx = (x2-x1)/(nx+1.)
            if FG.dx is not None:
                print "*** Warning: dx specified over-ridden by: ",dx
    
        if FG.ny is None:
            dy = FG.dy
            if dy is None:
                dy = dx
            ny = int(round((y2-y1)/dy)) + 1  
            if abs((ny-1)*dy + y1 - y2) > 1e-6:
                print "Warning: abs((ny-1)*dy + y1 - y2) = ", \
                      abs((ny-1)*dy + y1 - y2)
                print "         old y2: %22.16e" % y2
                y2 = y1 + dy*(ny-1)
                print "         resetting y2 to %22.16e" % y2
        else:
            ny = FG.ny
            dy = (y2-y1)/(ny+1.)
            if FG.dy is not None:
                print "*** Warning: dy specified over-ridden by: ",dy
    
    
        npts = nx*ny
    
        fid = open(FG.fname,'w')
        fid.write("%16.10e            # tstart_max\n"  % FG.tstart_max)
        fid.write("%16.10e            # tend_max\n"  % FG.tend_max)
        fid.write("%16.10e            # dt_check\n" % FG.dt_check)
        fid.write("%i %s              # min_level_check\n" \
                            % (FG.min_level_check,16*" "))

        fid.write("%16.10e            # arrival_tol\n" % FG.arrival_tol)
        fid.write("%i %s              # point_style\n" \
                            % (FG.point_style,16*" "))
    
        fid.write("%i  %i %s          # nx,ny\n" \
                            % (nx,ny,10*" "))
        fid.write("%16.10e   %20.10e            # x1, y1\n" % (x1,y1))
        fid.write("%16.10e   %20.10e            # x2, y2\n" % (x2,y2))
        fid.close()
        
    
        print "Created file ", FG.fname
        print "   specifying fixed grid with shape %i by %i, with  %i points" \
                % (nx,ny,npts)
        print "   lower left  = (%15.10f,%15.10f)" % (x1,y1)
        print "   upper right = (%15.10f,%15.10f)" % (x2,y2)
        print "   dx = %15.10e,  dy = %15.10e" % (dx,dy)
    
        xy = [x1,x2,y1,y2]
        fname_root = os.path.splitext(FG.fname)[0]
        kml_file = fname_root + '.kml'
        kmltools.box2kml(xy, kml_file, fname_root, color='8888FF')

    elif point_style==1:
        # 1d transect of points
        if FG.npts is None:
            dx = FG.dx
            npts = int(round(sqrt((x2-x1)**2 + (y2-y1)**2)/dx)) + 1
            if abs((npts-1)*dx + x1 - x2) > 1e-6:
                print "Warning: abs((npts-1)*dx + x1 - x2) = ", \
                      abs((npts-1)*dx + x1 - x2)
                x2 = x1 + dx*(npts-1)
                y2 = y1 + dx*(npts-1)
                print "         resetting x2 to %g" % x2
                print "         resetting y2 to %g" % y2
        else:
            npts = FG.npts
            dx = sqrt((x2-x1)**2 + (y2-y1)**2)/(npts+1.)
            if FG.dx is not None:
                print "*** Warning: dx specified over-ridden by: ",dx
    
    
        print "Creating 1d fixed grid with %s points" % npts
        print "   dx = %g" % dx
    
        fid = open(FG.fname,'w')
        fid.write("%g                 # tstart_max\n"  % FG.tstart_max)
        fid.write("%g                 # tend_max\n"  % FG.tend_max)
        fid.write("%g                 # dt_check\n" % FG.dt_check)
        fid.write("%i                 # min_level_check\n" % FG.min_level_check)
        fid.write("%g                 # arrival_tol\n" % FG.arrival_tol)
        fid.write("%g                 # point_style\n" % FG.point_style)
    
        fid.write("%i                 # npts\n" % (npts))
        fid.write("%g   %g            # x1, y1\n" % (x1,y1))
        fid.write("%g   %g            # x2, y2\n" % (x2,y2))
        fid.close()
        
    
        print "Created file ", FG.fname
        print "   specifying fixed grid with %i points equally spaced from " \
                % npts
        print "   (%g,%g)  to  (%g,%g)" % (x1,y1,x2,y2)
        
        # not yet implemented:
        #fname_root = os.path.splitext(FG.fname)[0]
        #kml_file = fname_root + '.kml'
        #kmltools.line2kml(xy, kml_file, fname_root, color='8888FF')

    elif point_style==3:
        # arbitrary quadrilateral
        x3,x4 = FG.x3, FG.x4
        y3,y4 = FG.y3, FG.y4
        if FG.n12 is None:
            raise NotImplementedError("Need to set n12 and n23")
        else:
            npts = FG.n12 * FG.n23
    
    
        fid = open(FG.fname,'w')
        fid.write("%g                 # tstart_max\n"  % FG.tstart_max)
        fid.write("%g                 # tend_max\n"  % FG.tend_max)
        fid.write("%g                 # dt_check\n" % FG.dt_check)
        fid.write("%i                 # min_level_check\n" % FG.min_level_check)
        fid.write("%g                 # arrival_tol\n" % FG.arrival_tol)
        fid.write("%g                 # point_style\n" % FG.point_style)
    
        fid.write("%i  %i %s          # FG.n12,FG.n23\n" \
                            % (FG.n12,FG.n23,10*" "))
        fid.write("%16.10e   %20.10e            # x1, y1\n" % (x1,y1))
        fid.write("%16.10e   %20.10e            # x2, y2\n" % (x2,y2))
        fid.write("%16.10e   %20.10e            # x3, y3\n" % (x3,y3))
        fid.write("%16.10e   %20.10e            # x4, y4\n" % (x4,y4))
        fid.close()
        
    
        print "Created file ", FG.fname
        print "   specifying fixed grid as a quadrilateral"
        print "       %i by %i, with  %i points" \
                % (FG.n12,FG.n23,npts)
        print "   corner 1 = (%15.10f,%15.10f)" % (x1,y1)
        print "   corner 2 = (%15.10f,%15.10f)" % (x2,y2)
        print "   corner 3 = (%15.10f,%15.10f)" % (x3,y3)
        print "   corner 4 = (%15.10f,%15.10f)" % (x4,y4)
        
        xy = [x1,y1,x2,y2,x3,y3,x4,y4]
        fname_root = os.path.splitext(FG.fname)[0]
        kml_file = fname_root + '.kml'
        kmltools.quad2kml(xy, kml_file, fname_root, color='8888FF')

