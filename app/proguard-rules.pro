# Keep Kotlinx Serialization generated serializers
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt

-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.vocalfox.app.domain.model.**$$serializer { *; }
-keepclassmembers class com.vocalfox.app.domain.model.** {
    *** Companion;
}
-keepclasseswithmembers class com.vocalfox.app.domain.model.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# Keep Sherpa-ONNX JNI classes if bundled
-keep class com.k2fsa.sherpa.onnx.** { *; }
