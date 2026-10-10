"""Read-only textured SCNE viewer with orbit, zoom and camera fitting."""
import math
import struct
from PySide6.QtCore import Qt
from PySide6.QtGui import QMatrix4x4, QVector3D, QImage, QSurfaceFormat, QVector4D
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram, QOpenGLTexture, QOpenGLFunctions_2_0
from PySide6.QtOpenGLWidgets import QOpenGLWidget


class SceneView(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        fmt = QSurfaceFormat()
        fmt.setVersion(2, 0)
        fmt.setDepthBufferSize(24)
        self.setFormat(fmt)
        self.setMinimumHeight(320)
        self.vertices = []
        self.batches = []
        self.material_images = {}
        self.gl_textures = {}
        self.automatic = True
        self.image = None
        self.dirty = True
        self.yaw, self.pitch, self.distance = 35., 25., 3.
        self.center = QVector3D()
        self.radius = 1.
        self.last = None
        self.program = None
        self.texture = None
        self.error = ''

    def set_meshes(self, meshes):
        self.vertices = []
        self.batches = []
        for mesh in meshes:
            start = len(self.vertices)
            self.vertices.extend(mesh['vertices'])
            self.batches.extend({**b, 'first':b['first']+start} for b in mesh.get('batches', [{'first':0,'count':len(mesh['vertices']), 'texture':None}]))
        self.fit_camera()
        self.dirty = True
        self.update()

    def set_material_images(self, images):
        self.material_images = images
        self.dirty = True
        self.update()

    def set_image(self, image):
        self.image = image
        self.dirty = True
        self.update()

    def fit_camera(self):
        if self.vertices:
            low = [min(v[k] for v in self.vertices) for k in range(3)]
            high = [max(v[k] for v in self.vertices) for k in range(3)]
            self.center = QVector3D(*[(a+b)/2 for a,b in zip(low, high)])
            self.radius = max(math.sqrt(sum((b-a)**2 for a,b in zip(low, high)))/2, .001)
        self.distance = 3.
        if self.vertices:
            angle, elevation = math.radians(self.yaw), math.radians(self.pitch)
            direction = QVector3D(math.cos(elevation)*math.sin(angle), math.sin(elevation), math.cos(elevation)*math.cos(angle))
            right = QVector3D.crossProduct(QVector3D(0,1,0), direction).normalized()
            up = QVector3D.crossProduct(direction, right).normalized()
            vertical = math.tan(math.radians(22.5))
            horizontal = vertical*max(self.width(),1)/max(self.height(),1)
            required = 0.
            for vertex in self.vertices:
                point = QVector3D(*vertex[:3])-self.center
                depth = QVector3D.dotProduct(point, direction)
                required = max(required,
                    depth+abs(QVector3D.dotProduct(point,right))/horizontal,
                    depth+abs(QVector3D.dotProduct(point,up))/vertical)
            self.distance = max(1.05, required/self.radius*1.10)
        self.update()

    def initializeGL(self):
        self.gl = QOpenGLFunctions_2_0()
        self.gl.initializeOpenGLFunctions()
        self.program = QOpenGLShaderProgram(self)
        vertex = """#version 110
        attribute vec3 position; attribute vec2 uv; attribute vec3 normal;
        uniform mat4 mvp; varying vec2 texcoord; varying float lighting;
        void main(){gl_Position=mvp*vec4(position,1.0);texcoord=uv;lighting=0.55+0.45*abs(dot(normalize(normal),normalize(vec3(0.4,1.0,0.3))));}"""
        fragment = """#version 110
        uniform sampler2D diffuse; uniform vec4 paletteTint; uniform bool usePalette; varying vec2 texcoord; varying float lighting;
        void main(){vec4 color=texture2D(diffuse,texcoord);if(color.a<0.1)discard;if(usePalette){vec3 low=color.rgb/12.92;vec3 high=pow((color.rgb+0.055)/1.055,vec3(2.4));vec3 linear=mix(low,high,step(vec3(0.04045),color.rgb))*paletteTint.rgb;vec3 encoded=mix(linear*12.92,1.055*pow(linear,vec3(1.0/2.4))-0.055,step(vec3(0.0031308),linear));color=vec4(encoded,color.a*paletteTint.a);}gl_FragColor=vec4(color.rgb*lighting,color.a);}"""
        if not (self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, vertex)
                and self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, fragment)
                and self.program.link()):
            self.error = self.program.log()
            return
        self.buffer = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
        self.buffer.create()
        self.dirty = True
        self.context().aboutToBeDestroyed.connect(self.cleanup)

    def cleanup(self):
        self.makeCurrent()
        if self.texture:
            self.texture.destroy()
            self.texture = None
        for texture in self.gl_textures.values():
            texture.destroy()
        self.gl_textures.clear()
        if hasattr(self, 'buffer'):
            self.buffer.destroy()
        self.doneCurrent()

    def paintGL(self):
        gl = self.gl
        gl.glClearColor(.08, .10, .14, 1.)
        gl.glClear(0x4000 | 0x0100)
        if self.error or not self.vertices:
            return
        if self.dirty:
            self.buffer.bind()
            packed = bytearray()
            for i in range(0, len(self.vertices), 3):
                a,b,c = self.vertices[i:i+3]
                u = [b[k]-a[k] for k in range(3)]
                v = [c[k]-a[k] for k in range(3)]
                normal = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
                length = math.sqrt(sum(x*x for x in normal))
                normal = [x/length for x in normal] if length else [0.,1.,0.]
                for vertex in (a,b,c):
                    packed.extend(struct.pack('8f', *vertex, *normal))
            data = bytes(packed)
            self.buffer.allocate(data, len(data))
            self.buffer.release()
            if self.texture:
                self.texture.destroy()
            image = self.image
            if image is None:
                image = QImage(1, 1, QImage.Format.Format_RGBA8888)
                image.fill(Qt.GlobalColor.lightGray)
            self.texture = QOpenGLTexture(image.mirrored(False, True))
            self.texture.setWrapMode(QOpenGLTexture.WrapMode.Repeat)
            self.texture.setMinificationFilter(QOpenGLTexture.Filter.Linear)
            self.texture.setMagnificationFilter(QOpenGLTexture.Filter.Linear)
            for texture in self.gl_textures.values():
                texture.destroy()
            self.gl_textures = {}
            for name, material_image in self.material_images.items():
                texture = QOpenGLTexture(material_image.mirrored(False, True))
                texture.setWrapMode(QOpenGLTexture.WrapMode.Repeat)
                texture.setMinificationFilter(QOpenGLTexture.Filter.Linear)
                self.gl_textures[name] = texture
            self.dirty = False
        gl.glEnable(0x0b71)
        gl.glDisable(0x0b44)
        angle, elevation = math.radians(self.yaw), math.radians(self.pitch)
        direction = QVector3D(math.cos(elevation)*math.sin(angle), math.sin(elevation), math.cos(elevation)*math.cos(angle))
        view = QMatrix4x4()
        view.lookAt(self.center + direction * (self.radius*self.distance), self.center, QVector3D(0,1,0))
        projection = QMatrix4x4()
        projection.perspective(45., max(self.width(),1)/max(self.height(),1), self.radius*.001, self.radius*100.)
        self.program.bind()
        self.program.setUniformValue('mvp', projection * view)
        self.program.setUniformValue('diffuse', 0)
        self.texture.bind(0)
        self.buffer.bind()
        for name, offset, size in [('position',0,3),('uv',12,2),('normal',20,3)]:
            self.program.enableAttributeArray(name)
            self.program.setAttributeBuffer(name, 0x1406, offset, size, 32)
        for batch in self.batches:
            texture = self.gl_textures.get(batch.get('texture'), self.texture) if self.automatic else self.texture
            texture.bind(0)
            tint = batch.get('palette_tint') if self.automatic else None
            self.program.setUniformValue('usePalette', tint is not None)
            self.program.setUniformValue('paletteTint', QVector4D(*(tint or (1.,1.,1.,1.))))
            gl.glDrawArrays(0x0004, batch['first'], batch['count'])
            texture.release()
        self.buffer.release()
        self.texture.release()
        self.program.release()

    def mousePressEvent(self, event):
        self.last = event.position()

    def mouseMoveEvent(self, event):
        if self.last is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self.last
            self.yaw += delta.x()*.5
            self.pitch = max(-89., min(89., self.pitch + delta.y()*.5))
            self.update()
        self.last = event.position()

    def wheelEvent(self, event):
        self.distance = max(1.05, min(40., self.distance * math.exp(-event.angleDelta().y()/1200)))
        self.update()
