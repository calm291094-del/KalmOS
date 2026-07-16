#!/usr/bin/env python3
"""Clima - Usa API pública de wttr.in"""
import os
import urllib.request
import json

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        clear()
        print("🌤️ CLIMA")
        print("=" * 30)
        
        ciudad = input("Ciudad (ej: Madrid, London, New York): ").strip()
        if not ciudad:
            print("❌ Ciudad no especificada")
            return
        
        print("\n⏳ Consultando clima...")
        
        url = f"https://wttr.in/{ciudad}?format=j1&lang=es"
        
        try:
            response = urllib.request.urlopen(url, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            current = data.get('current_condition', [{}])[0]
            location = data.get('nearest_area', [{}])[0]
            
            temp = current.get('temp_C', 'N/A')
            temp_f = current.get('temp_F', 'N/A')
            desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
            hum = current.get('humidity', 'N/A')
            wind = current.get('windSpeedKmph', 'N/A')
            feels = current.get('FeelsLikeC', 'N/A')
            
            clear()
            print("🌤️ CLIMA")
            print("=" * 50)
            print(f"\n📍 {location.get('areaName', [{}])[0].get('value', 'N/A')}, {location.get('country', [{}])[0].get('value', 'N/A')}")
            print(f"\n🌡️ Temperatura: {temp}°C / {temp_f}°F")
            print(f"🌡️ Sensación: {feels}°C")
            print(f"☁️  {desc}")
            print(f"💧 Humedad: {hum}%")
            print(f"💨 Viento: {wind} km/h")
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"❌ Error consultando clima: {e}")
        
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n¡Cancelado!")

if __name__ == "__main__":
    main()