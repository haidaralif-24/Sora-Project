import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import type { GLTF } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRMUtils, VRM } from '@pixiv/three-vrm'

export default function VrmViewer() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const w = canvas.clientWidth
    const h = canvas.clientHeight

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(30, w / h, 0.1, 20)
    camera.position.set(0, 1.3, 2.5)

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true })
    renderer.setSize(w, h)
    renderer.setPixelRatio(window.devicePixelRatio)

    const light = new THREE.DirectionalLight(0xffffff, Math.PI)
    light.position.set(1, 1, 1)
    scene.add(light)
    scene.add(new THREE.AmbientLight(0xffffff, 0.3))

    const loader = new GLTFLoader()
    loader.register((parser) => new VRMLoaderPlugin(parser))

    let vrm: VRM | null = null
    loader.load('/avatar.vrm', (gltf: GLTF) => {
      const loaded = gltf.userData.vrm as VRM
      VRMUtils.rotateVRM0(loaded)
      scene.add(loaded.scene)
      vrm = loaded
    })

    const clock = new THREE.Clock()
    let animId: number
    function animate() {
      animId = requestAnimationFrame(animate)
      const delta = clock.getDelta()
      if (vrm) vrm.update(delta)
      renderer.render(scene, camera)
    }
    animate()

    function onResize() {
      const c = canvasRef.current!
      const cw = c.clientWidth
      const ch = c.clientHeight
      renderer.setSize(cw, ch)
      camera.aspect = cw / ch
      camera.updateProjectionMatrix()
    }
    window.addEventListener('resize', onResize)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', onResize)
      renderer.dispose()
    }
  }, [])

  return (
    <canvas ref={canvasRef} style={{ width: '100vw', height: '100vh', display: 'block' }} />
  )
}
