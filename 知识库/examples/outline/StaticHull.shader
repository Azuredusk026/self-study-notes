Shader "KnowledgeBase/StaticHull"
{
    Properties
    {
        _OutlineColor ("Outline Color", Color) = (0.03, 0.03, 0.03, 1)
        _OutlineWidthOS ("Width in Object Units", Float) = 0.02
    }
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }
        Pass
        {
            Name "Outline"
            Tags { "LightMode" = "SRPDefaultUnlit" }
            Cull Front
            ZWrite Off
            ZTest LEqual
            HLSLPROGRAM
            #pragma vertex OutlineVert
            #pragma fragment OutlineFrag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _OutlineColor;
                float _OutlineWidthOS;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
            };

            Varyings OutlineVert(Attributes input)
            {
                Varyings output;
                float3 directionOS = normalize(input.normalOS);
                float3 positionOS = input.positionOS.xyz
                                    + directionOS * _OutlineWidthOS;
                output.positionCS = TransformObjectToHClip(positionOS);
                return output;
            }

            float4 OutlineFrag(Varyings input) : SV_Target
            {
                return _OutlineColor;
            }
            ENDHLSL
        }
    }
}
