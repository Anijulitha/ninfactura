from ninfactura.ninfactura_app import app

if _name_ == '_main_':
    app.run(debug=True, port=5001)