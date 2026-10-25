#!/usr/bin/env python3
"""Native PATTERN ABI in a texture-free GLES pbuffer. Mesa is not Pi qualification."""
import ctypes
import os
from pathlib import Path
os.environ.setdefault('PYOPENGL_PLATFORM', 'egl')
os.environ.setdefault('EGL_PLATFORM', 'surfaceless')
from OpenGL import EGL, GL
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

class Renderer:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.display = EGL.eglGetDisplay(EGL.EGL_DEFAULT_DISPLAY)
        major, minor = EGL.EGLint(), EGL.EGLint()
        EGL.eglInitialize(self.display, major, minor)
        attrs = (EGL.EGLint * 13)(EGL.EGL_SURFACE_TYPE, EGL.EGL_PBUFFER_BIT,
            EGL.EGL_RENDERABLE_TYPE, EGL.EGL_OPENGL_ES2_BIT,
            EGL.EGL_RED_SIZE, 8, EGL.EGL_GREEN_SIZE, 8, EGL.EGL_BLUE_SIZE, 8,
            EGL.EGL_ALPHA_SIZE, 8, EGL.EGL_NONE)
        config, count = EGL.EGLConfig(), EGL.EGLint()
        EGL.eglChooseConfig(self.display, attrs, ctypes.byref(config), 1, count)
        if count.value < 1: raise RuntimeError('No EGL ES2 pbuffer configuration')
        EGL.eglBindAPI(EGL.EGL_OPENGL_ES_API)
        self.surface = EGL.eglCreatePbufferSurface(self.display, config,
            (EGL.EGLint * 5)(EGL.EGL_WIDTH, width, EGL.EGL_HEIGHT, height, EGL.EGL_NONE))
        self.context = EGL.eglCreateContext(self.display, config, EGL.EGL_NO_CONTEXT,
            (EGL.EGLint * 3)(EGL.EGL_CONTEXT_CLIENT_VERSION, 2, EGL.EGL_NONE))
        EGL.eglMakeCurrent(self.display, self.surface, self.surface, self.context)
        self.info = {k: GL.glGetString(v).decode() for k, v in
            [('renderer', GL.GL_RENDERER), ('version', GL.GL_VERSION)]}
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_DITHER)
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        vertices = np.array([[-1,-1], [1,-1], [-1,1], [1,1]], dtype=np.float32)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        self.vertex = self.compile(GL.GL_VERTEX_SHADER, (ROOT / 'tools/native.vert').read_text())
        self.program = None
        GL.glViewport(0, 0, width, height)

    @staticmethod
    def compile(kind, source):
        shader = GL.glCreateShader(kind)
        GL.glShaderSource(shader, '#version 100\n' + source)
        GL.glCompileShader(shader)
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            raise RuntimeError(GL.glGetShaderInfoLog(shader).decode())
        return shader

    def load(self, path):
        if self.program: GL.glDeleteProgram(self.program)
        frag = self.compile(GL.GL_FRAGMENT_SHADER, path.read_text())
        self.program = GL.glCreateProgram()
        GL.glAttachShader(self.program, self.vertex)
        GL.glAttachShader(self.program, frag)
        GL.glBindAttribLocation(self.program, 0, 'position')
        GL.glLinkProgram(self.program)
        GL.glDeleteShader(frag)
        if not GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS):
            raise RuntimeError(GL.glGetProgramInfoLog(self.program).decode())
        GL.glUseProgram(self.program)
        self.uniforms = {s: GL.glGetUniformLocation(self.program, s) for s in
            ['u_resolution','u_x0','u_x1','u_x2','u_time','modelViewProjectionMatrix']}
        for name, location in self.uniforms.items():
            assert location >= 0, (path.name, 'Inactive required control', name)
        GL.glUniform2f(self.uniforms['u_resolution'], self.width, self.height)
        GL.glUniformMatrix4fv(self.uniforms['modelViewProjectionMatrix'], 1, False,
                             np.eye(4, dtype=np.float32))
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 8, ctypes.c_void_p(0))
        count = GL.glGetProgramiv(self.program, GL.GL_ACTIVE_UNIFORMS)
        active = {GL.glGetActiveUniform(self.program, i)[0].decode() for i in range(count)}
        assert active == set(self.uniforms), (path.name, active)

    def draw(self, knobs=(.5, .5, .5), seconds=0):
        for name, value in zip(['u_x0','u_x1','u_x2'], knobs):
            GL.glUniform1f(self.uniforms[name], value)
        GL.glUniform1f(self.uniforms['u_time'], seconds)
        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

    def pixels(self):
        data = GL.glReadPixels(0, 0, self.width, self.height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        rgba = np.frombuffer(data, np.uint8).reshape(self.height, self.width, 4)
        assert (rgba[:,:,3] == 255).all(), 'Output alpha is not opaque'
        return np.flipud(rgba[:,:,:3]).copy()

    def close(self):
        if self.program: GL.glDeleteProgram(self.program)
        GL.glDeleteShader(self.vertex)
        GL.glDeleteBuffers(1, [self.vbo])
        EGL.eglMakeCurrent(self.display, EGL.EGL_NO_SURFACE, EGL.EGL_NO_SURFACE, EGL.EGL_NO_CONTEXT)
        EGL.eglDestroyContext(self.display, self.context)
        EGL.eglDestroySurface(self.display, self.surface)
        EGL.eglTerminate(self.display)
