/// Demo payload for .diy container round-trip tests.

#if defined(_WIN32)
#  define DIY_PAYLOAD_API extern "C" __declspec(dllexport)
#else
#  define DIY_PAYLOAD_API extern "C"
#endif

/// Return the payload identity string.
DIY_PAYLOAD_API const char* diy_payload_info() {
    return "diy-payload/1.0";
}

/// Return a fixed value for minimal functional checks.
DIY_PAYLOAD_API int diy_payload_answer() {
    return 42;
}
