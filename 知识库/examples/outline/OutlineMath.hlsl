// API-independent mechanisms. Column-vector matrices: mul(matrix, vector).
float4 OffsetOutlinePixels(float4 clipPosition, float2 pixelDirection,
                           float widthPixels, float2 renderSize)
{
    float lengthSquared = dot(pixelDirection, pixelDirection);
    if (lengthSquared < 1e-8)
    {
        return clipPosition;
    }
    float2 direction = pixelDirection * rsqrt(lengthSquared);
    clipPosition.xy += direction * (2.0 * widthPixels / renderSize)
                       * clipPosition.w;
    return clipPosition;
}

float OutlineRelativeDepth(float centerDepth, float neighborDepth,
                          float minimumScale)
{
    return abs(neighborDepth - centerDepth)
           / max(min(centerDepth, neighborDepth), minimumScale);
}

float OutlineNormalEdge(float3 centerNormal, float3 neighborNormal)
{
    return 1.0 - clamp(dot(normalize(centerNormal), normalize(neighborNormal)),
                       -1.0, 1.0);
}

float3 CompositeOutline(float3 sceneColor, float3 lineColor, float mask)
{
    return lerp(sceneColor, lineColor, saturate(mask));
}
