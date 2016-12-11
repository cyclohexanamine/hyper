import sys, pygame, pygame.gfxdraw, time
from math import cos, sin, acos, atan2, pi, sinh, cosh, acosh, sqrt, fabs, copysign

scale = 0.02
npoints = 3
speed = 10
screen_size = 1000, 700



### Maths ###

## The hyperbolic plane is characterised by polar coordinates (r,a),
## the radial length and angle from horizontal. Geometry is done on
## these vectors using procedures derived from hyperbolic triangles,
## as in addp() and subp(). They are then converted to Cartesian vectors
## directly to be displayed as in ptoc(), which is the hyperboloid model.

## Add two polar vectors hyperbolically (k = 1).
##
## We use the hyperbolic law of cosines:
##   cosh c = cosh a cosh b - sinh a sinh b cos C
## where a and b are the sides of a triangle corresponding to p1 and p2,
## and c is the result of their sum. The angle C is, geometrically,
##   C = pi + a1 - a2
## so cos C = - cos(a2-a1). A similar procedure is carried out to find the
## angle B, where cos B = cos(a3-a1).
##
## For numerical stability, this bounds cosh c >=1, and -1 <= cos B <= 1.
## Additionally, we must recover the sign of B when we take acos(cos B);
## sign is worked out geometrically. We also prematurely exit when we
## encounter a degenerate case of r1, r2 or r3 being 0.
def addp(p1, p2):
    (r1,a1), (r2,a2) = p1, p2

    if not r1: return p2
    if not r2: return p1

    cr3 = cosh(r1)*cosh(r2) + sinh(r1)*sinh(r2)*cos(a2-a1)
    r3 = acosh(max(cr3,1))
    if not r3: return (0., 0.)

    ca3 = (cosh(r1)*cosh(r3) - cosh(r2))/(sinh(r1)*sinh(r3))
    sign = (1 if awrap(a2-a1) < pi else -1) * sgn(r1) * sgn(r1)
    a3 = a1 + sign*acos(max(-1,min(ca3, 1)))

    return r3, awrap(a3)

## Subtract two polar vectors hyperbolically (k = 1).
## In contrast to the above, we now have sides a and c of the triangle,
## and are looking for b. The side length is calculated in the same
## way, but the angle we want is different; here
##   A = a2 - a3
## so we look for cos A = cos(a3-a2).
def subp(p1, p2):
    (r1,a1), (r2,a2) = p1, p2

    if not r1: return (r2,a2 + pi)
    if not r2: return p1

    cr3 = cosh(r1)*cosh(r2) - sinh(r1)*sinh(r2)*cos(a2-a1)
    r3 = acosh(max(cr3,1))
    if not r3: return (0., 0.)

    ca3 = (cosh(r1) - cosh(r2)*cosh(r3))/(sinh(r2)*sinh(r3))
    sign = (-1 if awrap(a2-a1) < pi else 1) * sgn(r1) * sgn(r2)
    a3 = a2 + sign*acos(max(-1,min(ca3, 1)))

    return r3, awrap(a3)

## Polar to Cartesian vector
def ptoc(p):
    r, a = p
    x = r*cos(a)
    y = r*sin(a)
    return (x, y)

## Cartesian to polar vector
def ctop(c):
    x, y = c
    r = sqrt(x*x + y*y)
    a = atan2(y, x)
    return (r, a)

## Add two Cartesian vectors
def addc(c1, c2):
    (x1, y1), (x2, y2) = c1, c2
    return (x1 + x2, y1 + y2)

## Wrap an angle a to the range 0,2pi
def awrap(a):
    while a < 0: a += 2*pi
    while a > 2*pi: a -= 2*pi
    return a

## Map a polar vector to a screen position
def to_screen(p, screen_size):
    x, y = ptoc(p)

    screen_w, screen_h = screen_size
    screen_x = screen_w//2 + int(x/scale)
    screen_y = screen_h//2 - int(y/scale)

    return screen_x, screen_y

## Rasterise a hyperbolic line between p1 and p2. We parameterise the
## line by taking p(t) = p1 + (p2-p1)*t, with 0 <= t <= 1. Then we sample
## this line at a bit more than one pixel per sample.
def draw_line(screen, colour, p1, p2):
    screen_size = screen.get_size()
    l,a = subp(p2, p1)
    if l == 0: return

    p = lambda t: addp(p1, (t*l, a))
    dt = scale/l/2.
    for n in range(0, int(1/dt)):
        x,y = to_screen(p(n*dt), screen_size)
        pygame.gfxdraw.pixel(screen, x, y, colour)
        
## Sign function
def sgn(x): return copysign(1.,x)

## Get all distinct pairs of distinct elements in a list l
def pairs(l):
    res = []
    for ii in range(len(l)):
        for jj in range(ii+1, len(l)):
            res.append((l[ii],l[jj]))
    return res



### Logic ###

## Initialise objects, of the form [position, velocity], where both of 
## these are polar vectors. 
def initstate():
    return [[(0,0),(0,0)] for i in range(npoints)]

## Move a given object with the given key scheme (up,down,right,left)
def control(object, keys, scheme):
    v = scale*speed
    vel = (0, 0) # Cartesian
    if keys[scheme[0]]: vel = addc(vel, (0,  v))
    if keys[scheme[1]]: vel = addc(vel, (0, -v))
    if keys[scheme[2]]: vel = addc(vel, ( v, 0))
    if keys[scheme[3]]: vel = addc(vel, (-v, 0))
    object[0] = addp(object[0], ctop(vel))


def main():

    ## Globals

    keys = [False]*500 # keys that are down
    schemes = [ (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT)
              , (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
              , (pygame.K_i, pygame.K_k, pygame.K_l, pygame.K_j)
              ]

    black = 0, 0, 0
    white = 255, 255, 255


    ## Init

    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    screen.fill(white)

    objects = initstate()


    ## Main loop

    while 1:
        time.sleep(0.030)

        ## Events & controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN: keys[event.key] = True
            elif event.type == pygame.KEYUP: keys[event.key] = False

            if event.type==pygame.KEYDOWN and event.key == pygame.K_F5:
                # reset world
                screen.fill(white)
                objects = initstate()

        for ii in range(npoints): control(objects[ii], keys, schemes[ii])

        
        ## Graphics
        screen.fill(white)
        for object in objects: # draw a spot for each object
            pygame.draw.circle(screen, black, to_screen(object[0], screen_size), 2)
        for o1,o2 in pairs(objects): # draw a line between every pair of objects
            draw_line(screen, black, o1[0], o2[0])
        pygame.display.flip()


main()