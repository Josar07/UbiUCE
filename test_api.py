#!/usr/bin/env python3
"""
Script de prueba para el backend de navegación del campus
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    """Prueba el endpoint de salud"""
    print("🔍 Probando endpoint de salud...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose?")
        return False

def test_load_osm():
    """Prueba cargar un archivo OSM"""
    print("\n🗺️ Probando carga de archivo OSM...")
    try:
        # Intentar cargar un archivo de ejemplo
        data = {"osm_file_path": "campus.osm"}
        response = requests.post(f"{BASE_URL}/load-osm", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Archivo OSM cargado exitosamente")
                print(f"   {result.get('message', '')}")
                return True
            else:
                print(f"❌ Error cargando OSM: {result.get('message', '')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_graph_info():
    """Prueba obtener información del grafo"""
    print("\n📊 Probando información del grafo...")
    try:
        response = requests.get(f"{BASE_URL}/graph-info")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Información del grafo obtenida:")
                print(f"   Nodos: {result.get('nodes_count', 0)}")
                print(f"   Aristas: {result.get('edges_count', 0)}")
                bounds = result.get('bounds', {})
                if bounds:
                    print(f"   Límites: {bounds}")
                return True
            else:
                print(f"❌ Error: {result.get('message', '')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_calculate_route():
    """Prueba calcular una ruta"""
    print("\n🛣️ Probando cálculo de ruta...")
    try:
        # Coordenadas de ejemplo (ajustar según tu campus)
        data = {
            "startPoint": {
                "latitude": -0.1807,
                "longitude": -78.4678
            },
            "endPoint": {
                "latitude": -0.1808,
                "longitude": -78.4679
            },
            "algorithm": "dijkstra"
        }
        
        response = requests.post(f"{BASE_URL}/calculate-route", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                route = result.get('route', [])
                distance = result.get('distance', 0)
                duration = result.get('duration', 0)
                print("✅ Ruta calculada exitosamente:")
                print(f"   Puntos en la ruta: {len(route)}")
                print(f"   Distancia: {distance:.2f} metros")
                print(f"   Duración estimada: {duration} segundos")
                return True
            else:
                print(f"❌ Error calculando ruta: {result.get('message', '')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del backend de navegación del campus")
    print("=" * 60)
    
    # Ejecutar pruebas
    tests = [
        test_health,
        test_load_osm,
        test_graph_info,
        test_calculate_route
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Resumen
    print("=" * 60)
    print(f"📋 Resumen: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El backend está funcionando correctamente.")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 