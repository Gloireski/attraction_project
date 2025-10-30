import { Outlet, Link, NavLink, useNavigation } from "react-router"

export default function Layout() {
    const navigation = useNavigation()
    const isNavigating = navigation.state !== "idle"

    return (

        {/* Loading Bar */}
        {/* Loading Bar */}
      {isNavigating && (
        
      )}

      {/* Header */}
      
        
          
            
              🏛️ Attractions
            

            
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `transition-colors ${
                    isActive
                      ? "text-blue-600 font-semibold"
                      : "text-gray-600 hover:text-blue-600"
                  }`
                }
              >
                Home
              
              <NavLink
                to="/attractions"
                className={({ isActive }) =>
                  `transition-colors ${
                    isActive
                      ? "text-blue-600 font-semibold"
                      : "text-gray-600 hover:text-blue-600"
                  }`
                }
              >
                Attractions
              
              <NavLink
                to="/about"
                className={({ isActive }) =>
                  `transition-colors ${
                    isActive
                      ? "text-blue-600 font-semibold"
                      : "text-gray-600 hover:text-blue-600"
                  }`
                }
              >
                About
              
            
          
        
      

      {/* Main Content */}
      
        
      

      {/* Footer */}
      
        
          &copy; 2024 Attractions. All rights reserved.
        
      
    
  )
}
