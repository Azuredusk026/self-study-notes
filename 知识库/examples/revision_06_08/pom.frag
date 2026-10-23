#version 450
layout(location=0) in vec2 inputUV;
layout(location=1) in vec3 inputViewTS;
layout(location=0) out vec4 outputColor;
layout(binding=0) uniform sampler2D depthMap;
layout(std140,binding=1) uniform Parameters {
    vec2 uvDepthScale;
    int minLayers;
    int maxLayers;
    vec3 lightTS;
    int shadowSteps;
    float shadowBias;
    int isolatedPatch;
};

// Finite depth in [0,1], unit view pointing from surface toward camera, z>0.
// uvDepthScale converts a unit inward-depth interval to UV distance along T/B.
bool Outside(vec2 uv) { return any(lessThan(uv,vec2(0))) || any(greaterThan(uv,vec2(1))); }
struct PomHit { vec2 uv; float depth; bool valid; };
PomHit PomUV(vec2 origin, vec3 view, vec2 dx, vec2 dy) {
    if (isolatedPatch!=0 && Outside(origin)) return PomHit(origin,0.0,false);
    int layers = clamp(int(round(mix(float(maxLayers),float(minLayers),view.z))),1,128);
    vec2 ray = view.xy / max(view.z,0.05) * uvDepthScale;
    float before = textureGrad(depthMap,origin,dx,dy).r;
    if (before <= 0.0) return PomHit(origin,0.0,true);
    vec2 previous = origin;
    float previousDepth = 0.0;
    for (int i=1; i<=layers; ++i) {
        float depth = float(i)/float(layers);
        vec2 current = origin-ray*depth;
        if (isolatedPatch!=0 && Outside(current)) return PomHit(current,depth,false);
        float error = textureGrad(depthMap,current,dx,dy).r-depth;
        if (error <= 0.0) {
            float t = before/(before-error);
            return PomHit(mix(previous,current,t),mix(previousDepth,depth,t),true);
        }
        previous=current;
        previousDepth=depth;
        before=error;
    }
    return PomHit(origin-ray,1.0,true);
}

float HeightVisibility(PomHit hit, vec3 light, float qEnd, vec2 dx, vec2 dy) {
    if (!hit.valid) return 0.0;
    if (light.z<=0.0) return 0.0;
    qEnd=clamp(qEnd,0.0,hit.depth);
    if (qEnd<=0.0) return 1.0;
    vec2 ray=light.xy/max(light.z,0.05)*uvDepthScale;
    int steps=clamp(shadowSteps,1,128);
    float visibility=1.0;
    for (int i=1;i<=steps;++i) {
        float q=qEnd*float(i)/float(steps);
        vec2 uv=hit.uv+ray*q;
        if (isolatedPatch!=0 && Outside(uv)) break;
        if (hit.depth-q>textureGrad(depthMap,uv,dx,dy).r+shadowBias) {
            visibility=0.0;
            break;
        }
    }
    // Fade the finite-budget approximation to visible at grazing light angles.
    return mix(1.0,visibility,smoothstep(0.0,0.05,light.z));
}

void main() {
    vec2 dx=dFdx(inputUV),dy=dFdy(inputUV);
    vec3 view=normalize(inputViewTS);
    if (view.z<=0.0) { outputColor=vec4(inputUV,0,1); return; }
    PomHit hit=PomUV(inputUV,view,dx,dy);
    if (!hit.valid) discard;
    float visibility=HeightVisibility(hit,normalize(lightTS),hit.depth,dx,dy);
    outputColor=vec4(hit.uv,hit.depth,visibility); // RG = UV, B = depth, A = visibility
}
