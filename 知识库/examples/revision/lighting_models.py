"""对应光照模型文章的 CPU 参考；不模拟 GPU 资源或引擎管线。"""
import math


def ggx_d(noh, alpha):
    a2 = alpha * alpha
    return a2 / (math.pi * (noh * noh * (a2 - 1) + 1)**2)


def g1(mu, alpha):
    if mu <= 0:
        return 0
    return 2 * mu / (mu + math.sqrt(alpha**2 + (1-alpha**2)*mu**2))


def specular(v, l, alpha, f0):
    if v[2] <= 0 or l[2] <= 0:
        return 0
    h = tuple(a+b for a, b in zip(v, l))
    length = math.sqrt(sum(x*x for x in h))
    h = tuple(x/length for x in h)
    voh = max(0, min(1, sum(a*b for a, b in zip(v, h))))
    f = f0+(1-f0)*(1-voh)**5
    return ggx_d(h[2], alpha)*g1(v[2], alpha)*g1(l[2], alpha)*f/(4*v[2]*l[2])


def radical_inverse(i):
    value, scale = 0.0, .5
    while i:
        value += (i & 1)*scale
        scale *= .5
        i >>= 1
    return value


def integrate_lut(nov, alpha, count):
    """NDF 采半向量；拒绝样本保留在 count 分母中。"""
    v = (math.sqrt(max(0, 1-nov*nov)), 0, nov)
    a = b = 0.0
    for i in range(count):
        u, phi = (i+.5)/count, 2*math.pi*radical_inverse(i)
        noh = math.sqrt((1-u)/(1+(alpha*alpha-1)*u))
        s = math.sqrt(max(0, 1-noh*noh))
        h = (s*math.cos(phi), s*math.sin(phi), noh)
        voh = sum(x*y for x, y in zip(v, h))
        l = tuple(2*voh*x-y for x, y in zip(h, v))
        if voh <= 0 or l[2] <= 0:
            continue
        weight = g1(nov, alpha)*g1(l[2], alpha)*voh/(nov*noh)
        fc = (1-voh)**5
        a += weight*(1-fc)
        b += weight*fc
    return a/count, b/count


def rnm(base, detail):
    if base[2] < 0:
        raise ValueError('本文的基础法线限定在 +Z 半球')
    t = (base[0], base[1], base[2]+1)
    u = (-detail[0], -detail[1], detail[2])
    d = sum(x*y for x, y in zip(t, u))
    out = tuple(x*d/t[2]-y for x, y in zip(t, u))
    length = math.sqrt(sum(x*x for x in out))
    return tuple(x/length for x in out)


def annulus_energy(r0, r1, d, albedo):
    if not (0 <= r0 <= r1 and d > 0):
        raise ValueError('需要非负半径与正尺度')
    return albedo*(.25*(math.exp(-r0/d)-math.exp(-r1/d)) + .75*(math.exp(-r0/(3*d))-math.exp(-r1/(3*d))))


def projected_radius(radius_m, depth_m, vertical_fov, height_px):
    return radius_m * height_px/(2*math.tan(vertical_fov/2)*depth_m)
