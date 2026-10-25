#!/usr/bin/env python3
"""Compile and exercise real GLES shaders with isolated RGB8 feedback buffers.
Software Mesa validates behavior/compatibility, never Raspberry Pi performance.
"""
import ctypes
import os
from pathlib import Path
os.environ.setdefault('PYOPENGL_PLATFORM', 'egl')
os.environ.setdefault('EGL_PLATFORM', 'surfaceless')
from OpenGL import EGL, GL
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VERTEX = '''attribute vec4 position;
attribute vec2 texcoord;
uniform mat4 modelViewProjectionMatrix;
varying vec2 v_texcoord;
void main() { v_texcoord = texcoord; gl_Position = modelViewProjectionMatrix * position; }
'''

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
        if count.value < 1:
            raise RuntimeError('No EGL ES2 pbuffer configuration')
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
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        vertices = np.array([[-1,-1,0,0], [1,-1,1,0], [-1,1,0,1], [1,1,1,1]], dtype=np.float32)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        self.textures = GL.glGenTextures(3)
        for texture in self.textures:
            GL.glBindTexture(GL.GL_TEXTURE_2D, int(texture))
            for param, value in [(GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR),
                    (GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR),
                    (GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE),
                    (GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)]:
                GL.glTexParameteri(GL.GL_TEXTURE_2D, param, value)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, width, height, 0,
                           GL.GL_RGB, GL.GL_UNSIGNED_BYTE, None)
        self.fbos = GL.glGenFramebuffers(2)
        for fbo, texture in zip(self.fbos, self.textures[1:]):
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, int(fbo))
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0,
                GL.GL_TEXTURE_2D, int(texture), 0)
            if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
                raise RuntimeError('RGB8 framebuffer incomplete')
        self.vertex = self.compile(GL.GL_VERTEX_SHADER, VERTEX)
        self.program = None
        self.reset()

    @staticmethod
    def compile(kind, source):
        shader = GL.glCreateShader(kind)
        GL.glShaderSource(shader, '#version 100\n' + source)
        GL.glCompileShader(shader)
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            raise RuntimeError(GL.glGetShaderInfoLog(shader).decode())
        return shader

    def load(self, path):
        if self.program:
            GL.glDeleteProgram(self.program)
        frag = self.compile(GL.GL_FRAGMENT_SHADER, path.read_text())
        self.program = GL.glCreateProgram()
        GL.glAttachShader(self.program, self.vertex)
        GL.glAttachShader(self.program, frag)
        GL.glBindAttribLocation(self.program, 0, 'position')
        GL.glBindAttribLocation(self.program, 1, 'texcoord')
        GL.glLinkProgram(self.program)
        GL.glDeleteShader(frag)
        if not GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS):
            raise RuntimeError(GL.glGetProgramInfoLog(self.program).decode())
        GL.glUseProgram(self.program)
        self.uniforms = {s: GL.glGetUniformLocation(self.program, s) for s in
            ['u_tex0','u_tex1','u_resolution','u_x0','u_x1','u_x2','u_x3','u_time','ftime',
            'u_fx_knob3_available','u_fx_drift','modelViewProjectionMatrix']}
        GL.glUniform1i(self.uniforms['u_tex0'], 0)
        GL.glUniform1i(self.uniforms['u_tex1'], 1)
        GL.glUniform2f(self.uniforms['u_resolution'], self.width, self.height)
        GL.glUniformMatrix4fv(self.uniforms['modelViewProjectionMatrix'], 1, False,
                             np.eye(4, dtype=np.float32))
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        for index in [0,1]:
            GL.glEnableVertexAttribArray(index)
            GL.glVertexAttribPointer(index, 2, GL.GL_FLOAT, False, 16, ctypes.c_void_p(index*8))

    def reset(self, value=0):
        for fbo in self.fbos:
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, int(fbo))
            GL.glClearColor(value, value, value, 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.previous = 0

    def upload(self, source):
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, int(self.textures[0]))
        GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height,
                          GL.GL_RGB, GL.GL_UNSIGNED_BYTE, np.ascontiguousarray(source))

    def draw(self, knobs=(1, .55, .7), seconds=0, host_controls=False, drift=None):
        target = 1 - self.previous
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, int(self.fbos[target]))
        GL.glViewport(0, 0, self.width, self.height)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, int(self.textures[0]))
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, int(self.textures[self.previous+1]))
        for name, value in zip(['u_x0','u_x1','u_x2'], knobs):
            GL.glUniform1f(self.uniforms[name], value)
        GL.glUniform1f(self.uniforms['ftime'], seconds - int(seconds))
        GL.glUniform1f(self.uniforms['u_time'], seconds)
        GL.glUniform1f(self.uniforms['u_x3'], knobs[3] if len(knobs)>3 else 0.0)
        GL.glUniform1f(self.uniforms['u_fx_knob3_available'], float(host_controls))
        centre = drift if drift is not None else (.5+.44*np.sin(seconds*.07), .5+.44*np.sin(seconds*.093+1.3))
        GL.glUniform2f(self.uniforms['u_fx_drift'], *centre)
        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)
        self.previous = target

    def pixels(self):
        data = GL.glReadPixels(0, 0, self.width, self.height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        rgba = np.frombuffer(data, np.uint8).reshape(self.height, self.width, 4)
        assert (rgba[:,:,3] == 255).all(), 'Output alpha is not opaque'
        return rgba[:,:,:3].copy()

    def close(self):
        EGL.eglMakeCurrent(self.display, EGL.EGL_NO_SURFACE, EGL.EGL_NO_SURFACE, EGL.EGL_NO_CONTEXT)
        EGL.eglDestroyContext(self.display, self.context)
        EGL.eglDestroySurface(self.display, self.surface)
        EGL.eglTerminate(self.display)


def fixture(w, h, frame=0):
    y, x = np.mgrid[:h,:w].astype(np.float32)
    x, y = x/w, y/h
    circle = ((x - .5 - .18*np.sin(frame*.045))**2 + (y-.5)**2) < .075
    grid = ((np.floor(x*12) + np.floor(y*9)) % 2) * .25
    rgb = np.stack([.15+.65*x, .1+.6*y, .15+grid], axis=-1)
    rgb[circle] = [.95, .8, .3]
    rgb[(abs(x-.25)<.02) | (abs(y-.7)<.02)] = [.1,.9,1]
    return np.uint8(np.clip(rgb*255, 0, 255))
