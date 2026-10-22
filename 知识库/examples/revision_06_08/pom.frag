#version 450
layout(location=0) in vec2 inputUV;
layout(location=1) in vec3 inputViewTS;
layout(location=0) out vec4 outputColor;
layout(binding=0) uniform sampler2D depthMap;
layout(std140,binding=1) uniform Parameters {
    vec2 uvDepthScale;
    int minLayers;
    int maxLayers;
};

// Finite depth in [0,1], unit view pointing from surface toward camera, z>0.
// uvDepthScale converts a unit inward-depth interval to UV distance along T/B.
vec2 PomUV(vec2 origin, vec3 view, vec2 dx, vec2 dy) {
    int layers = clamp(int(round(mix(float(maxLayers),float(minLayers),view.z))),1,128);
    vec2 ray = view.xy / max(view.z,0.05) * uvDepthScale;
    float before = textureGrad(depthMap,origin,dx,dy).r;
    if (before <= 0.0) return origin;
    vec2 previous = origin;
    for (int i=1; i<=layers; ++i) {
        float depth = float(i)/float(layers);
        vec2 current = origin-ray*depth;
        float error = textureGrad(depthMap,current,dx,dy).r-depth;
        if (error <= 0.0) {
            float t = before/(before-error);
            return mix(previous,current,t);
        }
        previous=current;
        before=error;
    }
    return origin-ray;
}

void main() {
    vec2 dx=dFdx(inputUV),dy=dFdy(inputUV);
    vec3 view=normalize(inputViewTS);
    vec2 uv=inputUV;
    if (view.z>0.0) uv=PomUV(inputUV,view,dx,dy);
    outputColor=vec4(uv,0,1); // diagnostic UV, not a material or depth output
}
