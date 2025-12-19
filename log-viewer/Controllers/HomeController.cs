using Microsoft.AspNetCore.Mvc;

namespace LogViewer.Controllers;

public class HomeController : Controller
{
    public IActionResult Index()
    {
        return View();
    }
}
